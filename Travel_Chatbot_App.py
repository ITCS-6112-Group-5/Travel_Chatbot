# Main script for travel chatbot


import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Establish groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Set a default LLM model from Groq in session state
if "LLM_model" not in st.session_state:
    st.session_state["LLM_model"] = "llama-3.3-70b-versatile"

# Initialize chat history in session state
if "messages" not in st.session_state or st.session_state.messages is None:
    st.session_state.messages = []




# Chatbot --------------------------------------------------------------------------------

class Chatbot():
    def __init__(self):
        self.input_prompt = ""

        # chat_history to store all of the messages in the conversation.
        # Set the system prompt to establish the behavior of the chatbot.
        self.chat_history = [
                                {"role": "system", 
                                "content": "You are a travel assistant who helps provide information to users for planning trips."}
                            ]

        self.flight_info = ""
        self.hotel_info = ""
        self.location_info = ""
        self.general_info = ""

        # establish Groq client for API calls
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))



    def process_input(self, input_prompt:str):
        '''Determine if the user prompt is asking for information on flights, hotels, location, or general info.'''

        print("Running process_input function")

        self.input_prompt = input_prompt
        print(f"Input prompt: {self.input_prompt}")

        # make seperate chat history just for this process
        process_input_history = [{
                                    "role": "system", 
                                    "content": """You an AI assistant tasked with determining if the user's prompt is looking for the categories of 'flight', 'hotel', 'location', or 'general' information,
                                                Return only the names of the categories the prompt is asking about
                                                
                                                Here are some examples to follow:
                                                user: can you find flights to New York?
                                                assistant: flight

                                                user: what are hotels near popular tourist locations in Orlando?
                                                assistant: hotel location

                                                user: help me plan a trip from Charlotte to London.
                                                assistant: flight, hotel, location

                                                user: what is the tallest building in the world?
                                                assistant: general
                                                """
                                },
                                {
                                    "role": "user",
                                    "content": self.input_prompt
                                }]

        # completion = self.client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=process_input_history
        # )

        completion = self.client.chat.completions.create(
            model=st.session_state["LLM_model"],
            messages=process_input_history,
        )

        categories = str(completion.choices[0].message.content)
        print(f"Prompt Categories: {categories}")

        if ("flight" in categories):
            self.flight_agent()

        if ("hotel" in categories):
            self.hotel_agent()

        if ("location" in categories):
            self.location_agent()

        if ("general" in categories):
            self.general_info_agent()
        

        return self.return_results()
    

    def flight_agent(self):
        print("Running flight agent.")
        prompt = f"Use this user prompt to provide relevant information on flights: {self.input_prompt}"
        self.flight_info = self.call_llm(prompt = prompt)

    def hotel_agent(self):
        print("Running hotel agent.")
        prompt = f"Use this user prompt to provide relevant information on hotels: {self.input_prompt}"
        self.hotel_info = self.call_llm(prompt = prompt)

    def location_agent(self):
        print("Running location agent.")
        prompt = f"Use this user prompt to provide relevant information on the requested location: {self.input_prompt}"
        self.location_info = self.call_llm(prompt = prompt)

    def general_info_agent(self):
        print("Running general info agent.")
        prompt = f"Use this user prompt to provide relevant general information: {self.input_prompt}"
        self.location_info = self.call_llm(prompt = prompt)




    def call_llm(self, prompt):
        """function for general purpose LLM calls."""
        print("  Running call_llm.")

        # add user prompt to chat history
        self.chat_history.append({
                                    "role": "user",
                                    "content": prompt,
                                })

        # completion = self.client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=self.chat_history
        # )

        completion = self.client.chat.completions.create(
            model=st.session_state["LLM_model"],
            messages=self.chat_history,
        )

        return completion.choices[0].message.content
    

    def return_results(self):
        print("Running return results")
        return "\n\n" + str(self.flight_info) + str(self.hotel_info) + str(self.location_info)
    





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

        # Call LLM
        # LLM_response = client.chat.completions.create(
        #     model=st.session_state["LLM_model"],
        #     messages=st.session_state.messages,
        #     temperature=1,
        #     max_completion_tokens=1024,
        #     top_p=1,
        #     stop=None,
        # )

        # response = LLM_response.choices[0].message.content

        response = st.session_state.chatbot.process_input(prompt)

        # Display response in UI
        st.markdown(response)

    # Add response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})