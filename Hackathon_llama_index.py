import base64
import glob
import streamlit as st
import json
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import os
import logging as log
from typing import Any, cast
# imports
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import ( Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex )
from llama_index.core import VectorStoreIndex,ServiceContext,Document,SimpleDirectoryReader,StorageContext, load_index_from_storage
from llama_index.core.indices.query.query_transform.base import (
    StepDecomposeQueryTransform,
)
from llama_index.core.llms import LLM
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor.llm_rerank import LLMRerank
from llama_index.core.prompts import PromptTemplate
from llama_index.core.response_synthesizers import (
    ResponseMode,
    get_response_synthesizer,
)
from llama_index.core.schema import MetadataMode, NodeWithScore, QueryBundle, TextNode
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
# from llama_index.storage.docstore.firestore import FirestoreDocumentStore
from llama_index.utils.workflow import draw_all_possible_flows
from vertexai.generative_models import HarmBlockThreshold, HarmCategory, SafetySetting
import logging as log
import os
from dotenv import load_dotenv
import google.auth
import google.auth.transport.requests
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
log.basicConfig(filename="C:\\Users\\61087069\\OneDrive - LTIMindtree\\Desktop\\hackathon\\pythonProject1\\newfile.log",
                format='%(asctime)s %(message)s',filemode='w')

logger = log.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(log.DEBUG)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

Settings.llm =Gemini(
    model="models/gemini-1.5-flash-002",
    temperature=0.1
)
gemini_api_key = "470155914573"

embed_model = GeminiEmbedding(model_name="models/embedding-001")

st.set_page_config(page_title="Expert Adviser",layout="centered", initial_sidebar_state="auto", menu_items=None)

st.title(f"Expert Adviser")


def save_index(index, directory="./saved_index"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    index.storage_context.persist(persist_dir=directory)

if "messages" not in st.session_state.keys():
    st.session_state.messages=[
        {"role": "assistant", "content": "How can i help you?!"}
    ]



@st.cache_resource(show_spinner=False)
def load_data():
    index_directory = "./saved_index"
    if os.path.exists(index_directory):
        with st.spinner(text='Loading saved index...'):
            storage_context = StorageContext.from_defaults(persist_dir=index_directory)
            index = load_index_from_storage(storage_context)
    else:
        with st.spinner(text='Loading and indexing data...'):
            reader = SimpleDirectoryReader(input_dir="C:\\Users\\61087069\\OneDrive - LTIMindtree\\Desktop\\hackathon\\pythonProject1\\JSON", recursive=True)
            docs = reader.load_data()

            index = VectorStoreIndex.from_documents(docs, show_progress=True)
            save_index(index)
        index = VectorStoreIndex.from_documents(docs)
    return index

index = load_data()

if 'chat_engine' not in st.session_state.keys():
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True,
    )
    log.info("information comming from chat.engine")
    log.info(st.session_state.chat_engine)

if prompt :=st.chat_input("Your question"):
    st.session_state.messages.append({'role':'user','content':prompt})

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

if st.session_state.messages[-1]['role'] != 'assistant':
    with st.chat_message('assistant'):
        with st.spinner('thinking.....'):
            response = st.session_state.chat_engine.chat(prompt)
            log.info("details about prompt")
            log.info(prompt)
            st.write(response.response)
            message = {'role':'assistant','content':response.response}
            st.session_state.messages.append(message)


# st.header("Chat bot")
if __name__ == '__main__':
    pass

    # llm = Gemini(
    # model="models/gemini-1.5-flash-002",
    # # api_key="some key",  # uses GOOGLE_API_KEY env var by default
    # )
    #
    # from llama_index.llms.gemini import Gemini
    #
    # resp = llm.complete("Write a poem about a magic backpack")
    # print(resp)

