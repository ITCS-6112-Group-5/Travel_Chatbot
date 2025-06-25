# Script for the Streamlit Chatbot UI


import streamlit as st
import os
from chatbot_core import Chatbot

from dotenv import load_dotenv
load_dotenv()


# Initialize chat history in streamlit session state
if "messages" not in st.session_state or st.session_state.messages is None:
    st.session_state.messages = []


# Initialize chatbot object in streamlit session state
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
        response = st.session_state.chatbot.process_input(prompt) # type: ignore

        # Display response in UI
        st.markdown(response)

    # Add response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})