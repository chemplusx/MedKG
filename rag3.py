from __future__ import annotations
import os
from langchain_community.graphs import NebulaGraph
from langchain.chains import NebulaGraphQAChain
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.prompts.prompt import PromptTemplate

# from llama_hub.youtube_transcript import YoutubeTranscriptReader

import streamlit as st

from IPython.display import Markdown, display


CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}

Do not include any explanations in your responses.
Do not include any text except the generated Cypher statement.

The question is:
{question}"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

NEBULAGRAPH_EXTRA_INSTRUCTIONS = """
Instructions:


1. it requires explicit label specification only when referring to node properties: Like v.`protein`.name
3. it uses double equals sign for comparison: `==` rather than `=`
For instance:
```diff
< MATCH (p:protein)-[e:interaction]->(m:drug) WHERE m.name = 'The Godfather II'
< RETURN p.name, e.year, m.name;
---
> MATCH (p:`protein`)-[e:interation]->(m:`drug`) WHERE m.`drug`.`name` == 'The Godfather II'
> RETURN p.`protein`.`name`, e.year, m.`drug`.`name`;
```\n"""

NGQL_GENERATION_TEMPLATE = CYPHER_GENERATION_TEMPLATE.replace(
    "Generate Cypher", "Generate NebulaGraph Cypher"
).replace("Instructions:", NEBULAGRAPH_EXTRA_INSTRUCTIONS)

NGQL_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=NGQL_GENERATION_TEMPLATE
)




from typing import Any, Dict, List, Optional

from langchain_community.graphs.nebula_graph import NebulaGraph
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.pydantic_v1 import Field

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains.graph_qa.prompts import CYPHER_QA_PROMPT
from langchain.chains.llm import LLMChain

class MyChain(Chain):
    """Chain for question-answering against a graph by generating nGQL statements.

    *Security note*: Make sure that the database connection uses credentials
        that are narrowly-scoped to only include necessary permissions.
        Failure to do so may result in data corruption or loss, since the calling
        code may attempt commands that would result in deletion, mutation
        of data if appropriately prompted or reading sensitive data if such
        data is present in the database.
        The best way to guard against such negative outcomes is to (as appropriate)
        limit the permissions granted to the credentials used with this tool.

        See https://python.langchain.com/docs/security for more information.
    """

    graph: NebulaGraph = Field(exclude=True)
    ngql_generation_chain: LLMChain
    qa_chain: LLMChain
    input_key: str = "query"  #: :meta private:
    output_key: str = "result"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        """Return the input keys.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys.

        :meta private:
        """
        _output_keys = [self.output_key]
        return _output_keys

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        *,
        qa_prompt: BasePromptTemplate = CYPHER_QA_PROMPT,
        ngql_prompt: BasePromptTemplate = NGQL_GENERATION_PROMPT,
        **kwargs: Any,
    ) -> NebulaGraphQAChain:
        """Initialize from LLM."""
        qa_chain = LLMChain(llm=llm, prompt=qa_prompt)
        ngql_generation_chain = LLMChain(llm=llm, prompt=ngql_prompt)

        return cls(
            qa_chain=qa_chain,
            ngql_generation_chain=ngql_generation_chain,
            **kwargs,
        )

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """Generate nGQL statement, use it to look up in db and answer question."""
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        question = inputs[self.input_key]

        schema = """
            Node properties: [{'tag': 'disease', 'properties': [('id', 'string'), ('name', 'string'), ('mondo_name', 'string'), ('mondo_definition', 'string'), ('umls_description', 'string'), ('orphanet_definition', 'string'), ('orphanet_prevalence', 'string'), ('orphanet_epidemiology', 'string'), ('orphanet_clinical_description', 'string'), ('orphanet_management_and_treatment', 'string'), ('mayo_symptoms', 'string'), ('mayo_causes', 'string'), ('mayo_risk_factors', 'string'), ('mayo_complications', 'string'), ('mayo_prevention', 'string'), ('mayo_see_doc', 'string'), ('source', 'string')]}, {'tag': 'drug', 'properties': [('id', 'string'), ('name', 'string'), ('description', 'string'), ('half_life', 'string'), ('indication', 'string'), ('mechanism_of_action', 'string'), ('protein_binding', 'string'), ('pharmacodynamics', 'string'), ('state', 'string'), ('atc_1', 'string'), ('atc_2', 'string'), ('atc_3', 'string'), ('atc_4', 'string'), ('category', 'string'), ('group', 'string'), ('pathway', 'string'), ('molecular_weight', 'string'), ('tpsa', 'string'), ('clogp', 'string'), ('source', 'string')]}, {'tag': 'protein', 'properties': [('id', 'string'), ('name', 'string'), ('source', 'string')]}]
            Edge properties: [{'edge': 'interaction', 'properties': [('relation', 'string'), ('display_relation', 'string')]}]
            Relationships: ['(:protein)-[:interaction]->(:protein)', '(:disease)-[:interaction]->(:protein)', '(:drug)-[:interaction]->(:protein)']
        """
        generated_ngql = self.ngql_generation_chain.run(
            {"question": question, "schema": schema}, callbacks=callbacks
        )

        _run_manager.on_text("Generated nGQL:", end="\n", verbose=self.verbose)
        _run_manager.on_text(
            generated_ngql, color="green", end="\n", verbose=self.verbose
        )
        try:
            parsed_ngql = generated_ngql.split('```')
            if len(parsed_ngql)>0:
                generated_ngql = parsed_ngql[1][parsed_ngql[1].index('MATCH'):]
        except:
            print("No cypher generated")
        print(self.graph.get_schema, "Final generated NGQL -----", generated_ngql)
        generated_ngql = generated_ngql.replace('\n', ' ')
        context = self.graph.query(generated_ngql)

        _run_manager.on_text("Full Context:", end="\n", verbose=self.verbose)
        _run_manager.on_text(
            str(context), color="green", end="\n", verbose=self.verbose
        )

        result = self.qa_chain(
            {"question": question, "context": context},
            callbacks=callbacks,
        )
        return {self.output_key: result[self.qa_chain.output_key]}


os.environ["GRAPHD_HOST"] = "192.168.0.115"
os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula" 
os.environ["NEBULA_ADDRESS"] = "192.168.0.115:9669" 

graph = NebulaGraph( 
    space="prime_kg_1",
    username="root",
    password="nebula",
    address="192.168.0.115",
    port=9669,
    session_pool_size=30,
)

print(graph.get_schema)

chain = MyChain.from_llm(
    LlamaCpp(model_path= '/mnt/d/workspace/text-generation-webui/models/Meta-Llama-3-8B-Instruct.Q8_0.gguf',
        verbose=True,
        temperature=0,
        context_window=8192,
        n_ctx=8192,
        n_gpu_layers= 256,
    ), 
    graph=graph, verbose=True,
    ngql_prompt=NGQL_GENERATION_PROMPT,

)

while True:
    tt = input("Enter your query")
    print("Running chain: ", chain.run(tt)) #"What interacts with protein PHYHIP and how?"))



driver.execute_query("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
...         "RETURN friend.name ORDER BY friend.name",
...         name=name, database_="neo4j", routing_=RoutingControl.READ,
...     )


URI = "neo4j://localhost:7475"
AUTH = ("neo4j", "password")