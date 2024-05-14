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

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.output_parsers import StrOutputParser
from llama_cpp import ChatCompletionRequestMessage, ChatCompletionRequestSystemMessage, ChatCompletionRequestUserMessage

token = "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"

HfFolder.save_token(token)

os.environ['OPENAI_API_KEY'] = "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"
URI = "neo4j://192.168.0.115:7687"
AUTH = ("neo4j", "password")

em = HuggingFaceEmbeddings(model_name='BAAI/bge-large-en-v1.5')

retrieval_query_protein = """
       RETURN node.name as text, score, node{.*, embedding: Null, movies: movies} as metadata
"""
retrieval_query_drug = """
       RETURN node.name as text, score, node{.*, embedding: Null, movies: movies} as metadata
"""
retrieval_query_disease = """
       RETURN node.name as text, score, node{.*, embedding: Null, movies: movies} as metadata
"""

vector_index = Neo4jVector.from_existing_graph(
    em,
    url=URI,
    username="neo4j",
    password="password",
    index_name='Protein',
    keyword_index_name='protein_name',
    node_label="protein",
    text_node_properties=['name', 'description', 'source'],
    embedding_node_property='embedding',
    search_type='hybrid',
)

vector_index2 = Neo4jVector.from_existing_graph(
    em,
    url=URI,
    username="neo4j",
    password="password",
    index_name='Drug',
    keyword_index_name='drug_description',
    node_label="drug",
    text_node_properties=['name','description', 'half_life', 'indication', 'mechanism_of_action', 'protein_binding', 'pharmacodynamics', 'state', 'atc_1', 'atc_2', 'atc_3', 'atc_4',
        'category', 'group', 'pathway', 'molecular_weight', 'tpsa', 'clogp'],
    embedding_node_property='embedding',
    search_type='hybrid'
)

vector_index3 = Neo4jVector.from_existing_graph(
    em,
    url=URI,
    username="neo4j",
    password="password",
    index_name='Disease',
    keyword_index_name='disease_description',
    node_label="disease",
    text_node_properties=['mondo_name', 'mondo_definition', 'umls_description', 'orphanet_definition', 'orphanet_prevalence', 'orphanet_epidemiology', 'orphanet_clinical_description', 'orphanet_management_and_treatment', 'mayo_symptoms', 'mayo_causes', 'mayo_risk_factors', 'mayo_complications', 'mayo_prevention', 'mayo_see_doc'],
    embedding_node_property='embedding',
    search_type='hybrid'
)

vector_index.similarity_search()


llm = ChatOllama(
    model='local_llama_3', 
    temperature=0.1, 
    system="You are a medical chat assistant who answers user queries based on the context provided. Keep the response precise and include all the requested information. Do not apologise or repeat responses. In case you dont know the answer, Say `Apologies, I do not know the answer to this query.",  
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)
# llm = LlamaCpp(
#     model_path='D:\workspace\\text-generation-webui\models\Meta-Llama-3-8B-Instruct.Q8_0.gguf', 
#     temperature=0, 
#     n_batch=512, 
#     n_ctx=8192, 
#     n_gpu_layers=256, 
#     max_tokens=2048,
    
#     callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
# )

def get_alpha_value(alpha, base):
    '''
    Gets alpha_value from alpha_value and rope_freq_base
    '''
    if base > 0:
        return (base / 10000.) ** (63 / 64.)
    else:
        return alpha


def get_rope_freq_base(alpha, base):
    '''
    Gets rope_freq_base from alpha_value and rope_freq_base
    '''
    if base > 0:
        return base
    else:
        return 10000 * alpha ** (64 / 63.)

params = {
    'model_path': 'D:\workspace\\text-generation-webui\models\Meta-Llama-3-8B-Instruct.Q8_0.gguf', #'/mnt/d/workspace/text-generation-webui/models/Meta-Llama-3-8B-Instruct.Q8_0.gguf',
    'n_ctx': 8192,
    'n_threads': None,
    'n_threads_batch': None,
    'n_batch': 512,
    'use_mmap': True,
    'use_mlock': False,
    'mul_mat_q': True,
    'numa': False,
    'n_gpu_layers': 256,
    'rope_freq_base': get_rope_freq_base(1, 500000),
    'tensor_split': None,
    'rope_freq_scale': 1.0 / 1,
    'offload_kqv': True,
    'split_mode': 1,
    'max_tokens': 100, 
    'stop':["###"], 
    'temperature':0.1, 
    'top_p':0.2, 
    'top_k':10, 
    'repeat_penalty':1
}

llm = Llama(
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    **params
)

llm("Do somthing")
vector_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_index2.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            "score_threshold": 0.5
        }
    )
)

cq = """You are a medical chat assistant who answers user queries based on the context provided. 
        Keep the response precise and include all the requested information. Do not apologise or repeat responses. 
        In case you dont know the answer, Say `Apologies, I do not know the answer to this query.`

        Context: {context}
    """
cqp = ChatPromptTemplate.from_messages(
    [
        ("system", cq), 
        MessagesPlaceholder(variable_name="chat_history"), 
        ("human", "{question}")
    ]
)


def get_chat_template(question):
    return [
        { "role": "system", "content": cq},
        { "role": "user", "content": "{question}"}
    ]

def generate_with_configs(input):
    return llm.create_chat_completion(input,
        max_tokens=512,
        temperature=0.1,
        top_p=0.1,
        min_p=0,
        typical_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        repeat_penalty=1.18,
        top_k=40,
        stream=True,
        seed=-1,
        tfs_z=1,
        mirostat_mode=0,
        mirostat_tau=1,
        mirostat_eta=0.1,
    )


contextualize_q_chain = cqp | llm | StrOutputParser()
contextualize_q_chain = get_chat_template | generate_with_configs | StrOutputParser()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def contextualized_question(input: dict):
    return input["question"]
    if input.get("chat_history"):
        return contextualize_q_chain
    else:
        return input["question"]


retriever1 = vector_index.as_retriever(
    search_type = "similarity_score_threshold",
    search_kwargs = {"k":6, 'score_threshold': 1.0}
)

retriever2 = vector_index2.as_retriever(
    search_type = "similarity_score_threshold",
    search_kwargs = {"k":6, 'score_threshold': 0.5}
)

retriever3 = vector_index3.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k":6}
).configurable_alternatives()

vector_index.similarity_search_with_score()

# context = contextualized_question | retriever1
# context2 = contextualized_question | retriever2
# context3 = contextualized_question | retriever3

# rag_chain = (
#     RunnablePassthrough.assign(
#         context = context | context2 | context3 | format_docs
#     )
#     | cqp 
#     | llm
# )

rag_chain = (
    RunnablePassthrough.assign(
        context = contextualized_question | retriever1 | format_docs
    )
    | cqp 
    | llm
)

rag_chain2 = (
    RunnablePassthrough.assign(
        context = contextualized_question | retriever2 | format_docs
    )
    | cqp 
    | llm
)

chat_history = []
question ="What happens in GM1 gangliosidosis?"

response = rag_chain.invoke(
    {
        "question": question,
        "chat_history": chat_history
    }
)

question ="What is the state of (1R,2R,3R,4S,5R)-4-(BENZYLAMINO)-5-(METHYLTHIO)CYCLOPENTANE-1,2,3-TRIOL."

def generate_with_configs(input):
    return llm.create_chat_completion(input,
        max_tokens=512,
        temperature=0.1,
        top_p=0.1,
        min_p=0,
        typical_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        repeat_penalty=1.18,
        top_k=40,
        stream=True,
        seed=-1,
        tfs_z=1,
        mirostat_mode=0,
        mirostat_tau=1,
        mirostat_eta=0.1,
    )

rag_chain2 = (
    RunnablePassthrough.assign(
        context = contextualized_question | retriever2 | format_docs
    )
    | get_chat_template 
    | generate_with_configs
)

response = rag_chain2.invoke(
    {
        "question": question,
        "chat_history": chat_history
    }
)


def generate():
    response = rag_chain2.invoke(
        {
            "question": question,
            "chat_history": chat_history
        }
    )
    t = next(response)
    while t:
        print(t["choices"][0]["delta"]["content"], end="")
        t = next(response)


