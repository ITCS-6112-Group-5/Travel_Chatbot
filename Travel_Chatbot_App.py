# Main script for travel chatbot


import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from chatbot_core import Chatbot

load_dotenv()

# Establish groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Set a default LLM model from Groq in session state
if "LLM_model" not in st.session_state:
    st.session_state["LLM_model"] = "llama-3.3-70b-versatile"

# Initialize chat history in session state
if "messages" not in st.session_state or st.session_state.messages is None:
    st.session_state.messages = []




# Initialize chatbot object in session state
if "chatbot" not in st.session_state or st.session_state.chatbot is None:
    st.session_state.chatbot = Chatbot()


# Streamlit ------------------------------------------------------------------------------

st.title("NaviBlu Travel Assistant")

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

        # Call shared chatbot logic
        response = st.session_state.chatbot.process_input(prompt, st.session_state["LLM_model"])

        # Display response in UI
        st.markdown(response)

    # Add response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})