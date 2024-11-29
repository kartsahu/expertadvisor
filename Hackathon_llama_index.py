import base64
import glob
import streamlit as st
import json
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import os
import logging as log
from typing import Any, cast

from llama_index.core import ( Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex )

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

import os
from dotenv import load_dotenv
import google.auth
import google.auth.transport.requests
from llama_index.llms.gemini import Gemini


gemini_api_key = "470155914573"
# st.header("Chat bot")
if __name__ == '__main__':

    llm = Gemini(
    model="models/gemini-1.5-flash-002",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
    )

    from llama_index.llms.gemini import Gemini

    resp = llm.complete("Write a poem about a magic backpack")
    print(resp)