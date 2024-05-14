import os
import json
import openai
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_index.core import (
    SimpleDirectoryReader,
    KnowledgeGraphIndex,
)
from llama_index.core import ServiceContext
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
# from llama_hub.youtube_transcript import YoutubeTranscriptReader

import streamlit as st

from IPython.display import Markdown, display

os.environ["GRAPHD_HOST"] = "192.168.0.115"
os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula" 
os.environ["NEBULA_ADDRESS"] = "192.168.0.115:9669" 

@st.cache_resource
def get_tokenizer_model(name, auth_token):
    # Create tokenizer
    tokenizer = AutoTokenizer.from_pretrained(name, use_auth_token=auth_token)

    # Create model
    model = AutoModelForCausalLM.from_pretrained(
        name,
        use_auth_token=auth_token,
        torch_dtype=torch.float16,
        rope_scaling={"type": "dynamic", "factor": 2},
        load_in_8bit=True,
    )

    return tokenizer, model


# space_name = "prime_kg"
# edge_types, rel_prop_names = ["interaction"], ["relation"]  #interaction(relation string, display_relation string)
# tags = ["protein", "drug", "disease"]
# tag_prop_names = ["name", "name", "name"]

space_name = "phillies_rag"
edge_types, rel_prop_names = ["relationship"], ["relationship"]
tags = ["entity"]

# HfFolder.save_token('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')

model = "astronomer-io/Llama-3-8B-Instruct-GPTQ-8-Bit"
auth_token = "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"

# tokenizer, model = get_tokenizer_model(model, auth_token)
# llm = HuggingFaceLLM(
#         model=model,
#         tokenizer=tokenizer,
#     )


llm = HuggingFaceLLM(
    model_name=model,
    # model_file="D:\workspace\\text-generation-webui\models\Meta-Llama-3-8B-Instruct.Q8_0.gguf"
    tokenizer_name=model,
    context_window=3900,
    max_new_tokens=256,
    generate_kwargs={
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 0.95,
    },
    device_map="auto",
    is_chat_model=True
)



    # Create and dl embeddings instance
embeddings = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)

# Create new service context instance
service_context = ServiceContext.from_defaults(
    chunk_size=1024, #llm=llm, embed_model=embeddings
    llm=llm, embed_model=embeddings #"local:BAAI/bge-base-en-v1.5"            
)

graph_store = NebulaGraphStore(
    space_name=space_name,
    edge_types=edge_types,
    rel_prop_names=rel_prop_names,
    tags=tags,
    # tag_prop_names=tag_prop_names
)
storage_context = StorageContext.from_defaults(graph_store=graph_store)


try:

    storage_context = StorageContext.from_defaults(persist_dir='./storage_graph', graph_store=graph_store)
    index = load_index_from_storage(
        storage_context=storage_context,
        service_context=service_context,
        max_triplets_per_chunk=15,
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,
        verbose=True,
    )
    index_loaded = True
except:
    index_loaded = False

if not index_loaded:
    # csv_loader = CSVLoader("/mnt/d/workspace/data/PrimeKG_data/dataverse_files/kg_giant.csv")
    # data = csv_loader.load()
    # documents = []
    # splitter = CharacterTextSplitter(separator="\n",
    #                                 chunk_size=500,
    #                                 chunk_overlap=0,
    #                                 length_function=len)
    # docs = splitter.split_documents(data)

    # # Assign a unique identifier to each document
    # for i, doc in enumerate(documents):
    #     new_doc = Document(
    #         page_content=doc.page_content,    )
    #     documents.append(new_doc)

    WikipediaReader = download_loader("WikipediaReader")
    loader = WikipediaReader()
    wiki_documents = loader.load_data(pages=['Philadelphia Phillies'], auto_suggest=False)
    print(f'Loaded {len(wiki_documents)} documents')

    # youtube_loader = YoutubeTranscriptReader()
    # youtube_documents = youtube_loader.load_data(ytlinks=['https://www.youtube.com/watch?v=k-HTQ8T7oVw'])    
    # print(f'Loaded {len(youtube_documents)} YouTube documents')

    index = KnowledgeGraphIndex.from_documents(
        wiki_documents,
        storage_context=storage_context,
        max_triplets_per_chunk=2,
        service_context=service_context,
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,
        include_embeddings=True,
    )

    index.storage_context.persist(persist_dir='./storage_graph')

graph_rag_retriever = KnowledgeGraphRAGRetriever(
    storage_context=storage_context,
    llm=llm,
    verbose=True,
)

# query_engine = RetrieverQueryEngine.from_args(
#     graph_rag_retriever,
#     llm=llm
# )

query_engine = index.as_query_engine(
    include_text=True,
    response_mode="tree_summarize",
    embedding_mode="hybrid",
    similarity_top_k=3,
    explore_global_knowledge=True,
)

# query_engine = index.as_query_engine()

response = query_engine.query("Tell me about Bryce Harper.")

# from IPython.display import display, Markdown

# response = query_engine.query(
#     "Tell me more about protein GPANK1",
# )
display(Markdown(f"<b>{resp}</b>"))