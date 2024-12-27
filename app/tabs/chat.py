import streamlit as st
from typing import List
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import TextNode, QueryBundle, NodeWithScore
from llama_index.core import Settings
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_cloud.client import AsyncLlamaCloud
from llama_cloud.types import Retriever
from utils import get_llamacloud_client, get_project_selector

class LlamaCloudCompositeRetriever(BaseRetriever):

    def __init__(self, client: AsyncLlamaCloud, retriever: Retriever) -> None:
        super().__init__()
        self.client = client
        self.retriever = retriever

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        raise NotImplementedError("Use aretrieve instead")

    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        results = await self.client.retrievers.retrieve(retriever_id=self.retriever.id, query=query_bundle.query_str)
        return [
            NodeWithScore(
                node=TextNode(
                    id_=retrieved_node.id,
                    text=retrieved_node.text,
                    metadata=retrieved_node.metadata
                ),
                score=1.0,
            )
            for retrieved_node in results.nodes
        ]

async def chat_tab():
    client = get_llamacloud_client()
    if client is None:
        st.write("Fill the form on the API Key tab first.")
        return
    openai.api_key = st.secrets.openai_key
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        system_prompt="You are a friendly Q&A Chatbot",
        api_key=st.secrets.openai_key,
    )
    st.title("Chat with a Composite Retriever")
    selected_project = await get_project_selector(client, "chat")
    retrievers = await client.retrievers.list_retrievers(project_id=selected_project.id)
    if not retrievers:
        st.write(f"No retrievers found under '{selected_project.name}' project. Create a composite retriever first on the 'Composite Retriever' tab.")
        return
    retrievers = sorted(retrievers, key=lambda r: r.name)
    selected_retriever = st.selectbox("Select Retriever", retrievers, format_func=lambda r: r.name, key="retriever_selector")


    st.session_state.messages = st.session_state.get(
        "messages",
        [
            {
                "role": "assistant",
                "content": "Ask me a question about the data ingested by the selected indices!",
            }
        ]
    )

    chat_engine: BaseChatEngine = st.session_state.get(
        "chat_engine",
        CondensePlusContextChatEngine.from_defaults(
            retriever=LlamaCloudCompositeRetriever(
                client=client,
                retriever=selected_retriever
            ),
            chat_history=st.session_state.messages,
            memory=ChatMemoryBuffer(token_limit=3000),
            llm=Settings.llm,
            verbose=True,
        ),
    )
    st.session_state.chat_engine = chat_engine

    if prompt := st.chat_input(
        "Ask a question"
    ):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:  # Write message history to UI
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response_stream = await chat_engine.achat(prompt)
            st.write(response_stream.response)
            message = {"role": "assistant", "content": response_stream.response}
            # Add response to message history
            st.session_state.messages.append(message)
