# Shared Chatbot logic for both Streamlit App and Website Dev
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Chatbot --------------------------------------------------------------------------------

class Chatbot:
    def __init__(self):
        # Ensure GROQ_API_KEY in .env file
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.chat_history = [
            {"role": "system", 
             "content": "You are a travel assistant who helps provide information to users for planning trips."}
        ]

    def process_input(self, input_prompt):
        categories = self.categorize_request(input_prompt)
        
        response = ""
        if "flight" in categories:
            response += self.get_flight_info(input_prompt) + "\n\n"
        if "hotel" in categories:
            response += self.get_hotel_info(input_prompt) + "\n\n"
        if "location" in categories:
            response += self.get_location_info(input_prompt) + "\n\n"
        if "general" in categories:
            response += self.get_general_info(input_prompt) + "\n\n"
        
        if not response.strip():
            response = self.call_llm(f"Provide helpful travel information for: {input_prompt}")
        
        return response.strip()

    def categorize_request(self, prompt):
        category_prompt = [
            {
                "role": "system", 
                "content": """You determine if the user wants 'flight', 'hotel', 'location', or 'general' travel information.
                            Return only the category names.
                            
                            Examples:
                            user: flights to New York?
                            assistant: flight
                            
                            user: hotels in Orlando?
                            assistant: hotel
                            
                            user: plan trip to London
                            assistant: flight, hotel, location"""
            },
            {"role": "user", "content": prompt}
        ]
        
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=category_prompt,
        )
        
        return completion.choices[0].message.content.lower()

    def get_flight_info(self, prompt):
        return self.call_llm(f"Provide flight information and booking tips for: {prompt}")
    
    def get_hotel_info(self, prompt):
        return self.call_llm(f"Provide hotel recommendations and booking advice for: {prompt}")
    
    def get_location_info(self, prompt):
        return self.call_llm(f"Provide destination information, attractions, and travel tips for: {prompt}")
    
    def get_general_info(self, prompt):
        return self.call_llm(f"Provide general travel advice and information for: {prompt}")

    def call_llm(self, prompt):
        messages = self.chat_history + [{"role": "user", "content": prompt}]
        
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
        )
        
        return completion.choices[0].message.content