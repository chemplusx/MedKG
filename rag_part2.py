import os
import json
import openai
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_index.core import (
    SimpleDirectoryReader,
    KnowledgeGraphIndex,
)
from llama_index.core import ServiceContext, PromptTemplate
# from llama_index.
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.langchain import LangchainEmbedding
# from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from llama_index.core import StorageContext, load_index_from_storage, download_loader
from llama_index.graph_stores.nebula import NebulaGraphStore
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from llama_index.core import set_global_service_context
from llama_index.core.query_engine import KnowledgeGraphQueryEngine

# from llama_hub.youtube_transcript import YoutubeTranscriptReader

import streamlit as st

from IPython.display import Markdown, display

os.environ["GRAPHD_HOST"] = "192.168.0.115"
os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula" 
os.environ["NEBULA_ADDRESS"] = "192.168.0.115:9669" 


class PromptEmbeddingKGRetriever(KnowledgeGraphRAGRetriever):
    custom_synthesis_prompt = (
    "Task:Generate Cypher statement to query a graph database.\n"
    "Instructions:\n"
    "Use only the provided relationship types and properties in the schema.\n"
    "Do not use any other relationship types or properties that are not provided.\n"
    "Schema:\n"
    "{schema}\n"
    "Note: Do not include any explanations or apologies in your responses.\n"
    "Do not respond to any questions that might ask anything else than for you "
    "to construct a Cypher statement. \n"
    "Do not include any text except the generated Cypher statement.\n"
    "\n"
    "The question is:\n"
    "{query_str}\n"
)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _retrieve(self, query, **kwargs):
        # Generate your custom prompt here
        custom_prompt = self.generate_custom_prompt(query)

        # Update the prompt
        self._kg_query_engine.update_prompts(
            {
                "graph_query_synthesis_prompt": custom_prompt
            }
        )

        # Call the original _retrieve method
        return super()._retrieve(query, **kwargs)

    def generate_custom_prompt(self, query):
        qa_prompt = PromptTemplate(self.custom_synthesis_prompt.format(schema=self._graph_schema, query_str=query))
        print(qa_prompt)
        return qa_prompt



graph_store = NebulaGraphStore(
    space_name='prime_kg_1',
    edge_types=['interaction'],
    rel_prop_names=['relation'],
    tags=['protein'],
)

model = "astronomer-io/Llama-3-8B-Instruct-GPTQ-8-Bit"
auth_token = "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"

llm = HuggingFaceLLM(
    model_name=model,
    tokenizer_name=model,
    context_window=3900,
    max_new_tokens=256,
    generate_kwargs={
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 0.95,
        # "do_sample": True
    },
    device_map="auto",
    is_chat_model=True
)



    # Create and dl embeddings instance
embeddings = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)

service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embeddings,
)

set_global_service_context(service_context)

storage_context = StorageContext.from_defaults(graph_store=graph_store)

kg_index = KnowledgeGraphIndex.from_documents(
    [],
    storage_context=storage_context,
    service_context=service_context,
    max_triplets_per_chunk=10,
    space_name='prime_kg_1',
    edge_types=['interaction'],
    rel_prop_names=['relation'],
    tags=['protein'],
    include_embeddings=True,
)

nl2kg_query_engine = KnowledgeGraphQueryEngine(
    storage_context=storage_context,
    service_context=service_context,
    llm=llm,
    verbose=True,
)

kg_rag_query_engine = kg_index.as_query_engine(
    include_text=False,
    retriever_mode="keyword",
    response_mode="tree_summarize",
)

kg_retriever = PromptEmbeddingKGRetriever(
    storage_context=storage_context,
    service_context=service_context,
    llm=llm,
    verbose=True,
    with_nl2graphquery=True
)

query_engine_with_nl2graphquery = RetrieverQueryEngine.from_args(
    kg_retriever, service_context=service_context
)

response = query_engine_with_nl2graphquery.query(
    "Tell me about drugs",
)
