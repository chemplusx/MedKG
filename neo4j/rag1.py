# import neo4j
# import langchain.embeddings
# import langchain.chat_models
# import langchain.prompts.chat

# langchain: ls__60cbfc0cba7c4afa9b49915abdc7e189

# emb = OpenAIEmbeddings() # VertexAIEmbeddings() or BedrockEmbeddings() or ...
# llm = ChatOpenAI() # ChatVertexAI() or BedrockChat() or ChatOllama() ...

# vector = emb.embed_query(user_input)

# vectory_query = """
# // find products by similarity search in vector index
# CALL db.index.vector.queryNodes('products', 5, $embedding) yield node as product, score

# // enrich with additional explicit relationships from the knowledge graph
# MATCH (product)-[:HAS_CATEGORY]->(cat), (product)-[:BY_BRAND]->(brand)
# MATCH (product)-[:HAS_REVIEW]->(review {rating:5})<-[:WROTE]-(customer) 

# // return relevant contextual information
# RETURN product.Name, product.Description, brand.Name, cat.Name, 
#        collect(review { .Date, .Text })[0..5] as reviews, score
# """

# records = neo4j.driver.execute_query(vectory_query, embedding = vector)
# context = format_context(records)

# template = """
# You are a helpful assistant that helps users find information for their shopping needs.
# Only use the context provided, do not add any additional information.
# Context:  {context}
# User question: {question}
# """

# chain = prompt(template) | llm

# answer = chain.invoke({"question":user_input, "context":context}).content



import os
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.llamacpp import LlamaCppEmbeddings
from langchain.embeddings.ollama import OllamaEmbeddings
# from langchain.embeddings.
from langchain.embeddings.huggingface import HuggingFaceEmbeddings, HuggingFaceBgeEmbeddings
from llama_cpp import Llama
from langchain.chat_models.ollama import ChatOllama
from langchain.llms.llamacpp import LlamaCpp
from langchain.chains import RetrievalQA
from huggingface_hub.hf_api import HfFolder

token = "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"

HfFolder.save_token(token)

os.environ['OPENAI_API_KEY'] = "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"
URI = "neo4j://192.168.0.115:7687"
AUTH = ("neo4j", "password")

em = HuggingFaceEmbeddings(model_name='meta-llama/Meta-Llama-3-8B-Instruct')
em = HuggingFaceEmbeddings(model_name='BAAI/bge-large-en-v1.5')

vector_index = Neo4jVector.from_existing_graph(
    em,
    url=URI,
    username="neo4j",
    password="password",
    index_name='Protein',
    node_label="protein",
    text_node_properties=['name', 'source'],
    embedding_node_property='embedding',
)

vector_index = Neo4jVector.from_existing_graph(
    em,
    url=URI,
    username="neo4j",
    password="password",
    index_name='Drug',
    node_label="drug",
    text_node_properties=['name','description', 'half_life', 'indication', 'mechanism_of_action', 'protein_binding', 'pharmacodynamics', 'state', 'atc_1', 'atc_2', 'atc_3', 'atc_4',
        'category', 'group', 'pathway', 'molecular_weight', 'tpsa', 'clogp'],
    embedding_node_property='embedding',
)

vector_index = Neo4jVector.from_existing_index(
    HuggingFaceEmbeddings(),
    url=URI,
    username="neo4j",
    password="password",
    index_name='Protein'
)

vector_index = Neo4jVector.from_existing_graph(
    LlamaCppEmbeddings(
        model_path="/mnt/d/workspace/text-generation-webui/models/Meta-Llama-3-8B-Instruct.fp16.bin",
    ),
    url=URI,
    username="neo4j",
    password="password",
    index_name='Protein',
    node_label="protein",
    text_node_properties=['name', 'source'],
    embedding_node_property='embedding',

)

vector_index.search()

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
vector_qa = RetrievalQA.from_chain_type(
    llm=ChatOllama(model='llama3', temperature=0.1,  callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])),
    chain_type="stuff",
    retriever=vector_index.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            "score_threshold": 0.5
        }
    )
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
cq = "You are a medical chat assistant who answers user queries based on the context provided. Keep the response precise and include all the requested information. Do not apologise or repeat responses. In case you dont know the answer, Say `Apologies, I do not know the answer to this query.`"
cqp = ChatPromptTemplate.from_messages(
    [
        ("system", cq), 
        MessagesPlaceholder(variable_name="chat_history"), 
        ("human", "{question}")
    ]
)

vector_qa = RetrievalQA.from_chain_type(
    llm=LlamaCpp(
        model_path='D:\workspace\\text-generation-webui\models\Meta-Llama-3-8B-Instruct.Q8_0.gguf',
        temperature=1, 
        n_batch=512,
        n_ctx=8192,
        n_gpu_layers=256,
        streaming=True),
    chain_type="stuff",
    retriever=vector_index.as_retriever()
)


vector_qa = RetrievalQA.from_chain_type(
    llm=LlamaCpp(
        model_path='/mnt/d/workspace/text-generation-webui/models/Meta-Llama-3-8B-Instruct.Q8_0.gguf',
        temperature=0, 
        n_batch=512,
        n_ctx=8192,
        n_gpu_layers=256,
        streaming=True),
    chain_type="stuff",
    retriever=vector_index.as_retriever()
)



rag_chain = (
    RunnablePassthrough.assign(
        context = contextualized_question | ret | format_docs
    )
    | cqp 
    | llm
)

question = "What is the usecase of montelukast drug?"
ai_msg = rag_chain.invoke(
    {
        "question": question,
        "chat_history": chat_history
    }
)

second_question = "What are its targets?"

rag_chain.invoke(
    {
        "question": second_question,
        "chat_history": chat_history
    }
)

def contextualized_question(input: dict):
    if input.get("chat_history"):
        return cqc
    else:
        return input["question"]