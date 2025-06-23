# Main script for travel chatbot

from openai import OpenAI
import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

st.title("NaviBlu Travel Assistant")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Set a default openai model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Set a default LLM model from Groq
if "LLM_model" not in st.session_state:
    st.session_state["LLM_model"] = "llama-3.3-70b-versatile"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type Here"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        # Display user query in UI
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Call LLM
        LLM_stream = client.chat.completions.create(
            model=st.session_state["LLM_model"],
            messages=st.session_state.messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
        )

        response = LLM_stream.choices[0].message.content

        #display response in UI
        st.markdown(response)

    # Add response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})