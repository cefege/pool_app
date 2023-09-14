# Imports
import os
import streamlit as st
import time
from string import Template
from embedchain import App
from embedchain.config import LlmConfig

__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


# Constants
OPENAI_API_KEY = st.secrets["API"]["OPEN_AI_API_KEY"]
TEMPLATE_STRING = """
Your task is to answer the questions based only the information given.
After the initial answer reinforce the answer with more details in the next sentences.
Do not add any information that is not in the text.
Write with Markdown.
Information: $context
Query: $query
Answer:
"""
NUMBER_DOCUMENTS = 40
MODEL_NAME = "gpt-4"
TEMPERATURE = 0
STREAM = False

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Create an instance of the App
pool_app = App()

# Create a Template instance with your custom string
custom_template = Template(TEMPLATE_STRING)


def display_existing_messages():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def add_user_message_to_session(prompt):
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


def create_query_config(template):
    """Create the configuration for the query."""
    return LlmConfig(
        number_documents=NUMBER_DOCUMENTS,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        template=template,
        stream=STREAM,
    )


def query_model(query):
    """Query the model with a specific string."""
    # Get the configuration for the query
    query_config = create_query_config(custom_template)

    # Query the model and return the result
    stream = pool_app.query(query, config=query_config)
    answer = ""

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        for chunk in stream:
            answer += chunk
            time.sleep(0.01)
            message_placeholder.markdown(answer + "▌")
        message_placeholder.markdown(answer)
    st.session_state["messages"].append({"role": "assistant", "content": answer})


# Streamlit UI
st.title("Chat with AI")
user_input = st.text_input("Enter your question:")
clicked = st.button("Submit")

display_existing_messages()
if clicked:
    add_user_message_to_session(user_input)
    query_model(user_input)
