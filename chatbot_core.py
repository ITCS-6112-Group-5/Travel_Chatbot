# Shared Chatbot logic for both Streamlit App and Website Dev
import os
import json
from amadeus import Client, ResponseError
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Chatbot --------------------------------------------------------------------------------

class Chatbot():
    def __init__(self):
        self.input_prompt = ""

        self.LLM_model = "llama-3.3-70b-versatile"

        self.amadeus = Client(
            client_id = os.getenv("AMADEUS_API_KEY"),
            client_secret = os.getenv("AMADEUS_API_SECRET")
        )

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
            model=self.LLM_model,
            messages=process_input_history, # type: ignore
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
        print("Running hotel agent.\n")

        prompt = f"""Use this user input to extract the hotel information the user is looking for: 
                user input: {self.input_prompt}
                format your response as a json exactly structured like below and nothing else. If you can't find information for a section, make an educated guess based on the chat history. 
                If no year is specified, assume that it is 2025.

                {{
                "city": three letter city iataCode,
                "checkInDate": "YYY-MM-DD",
                "checkOutDate": "YYY-MM-DD",
                "numGuests": X
                }}
                """
        
        search_info = self.call_llm(prompt = prompt)
        print(search_info)

        # convert to JSON
        search_info_json = json.loads(search_info) # type: ignore
        print(search_info_json)
        print()

        # # get the three letter city code
        # city_code = st.session_state.amadeus.reference_data.locations.cities.get(keyword=search_info_json.get("city")).data
        # print(city_code)
        # city_code = city_code[0].get("iataCode")
        # print(f"City Code: {city_code}\n")

        # Get list of hotels by city code
        hotel_response = self.amadeus.reference_data.locations.hotels.by_city.get(cityCode=search_info_json.get("city"))

        # Make list of hotel Ids
        hotel_ids = []
        for hotel in hotel_response.data:
            hotel_ids.append(str(hotel.get("hotelId")))
            print(hotel)

        print("\nHotel Ids:")
        print(hotel_ids)
        print(len(hotel_ids))

        hotel_offers = self.amadeus.shopping.hotel_offers_search.get(
            hotelIds = hotel_ids[0:20], # search through first number of hotel ids
            checkInDate = search_info_json.get("checkInDate"),
            checkOutDate = search_info_json.get("checkOutDate"),
            adults = search_info_json.get("numGuests")
        )

        print("\nHotel offers:")
        print(type(hotel_offers))
        print(type(hotel_offers.data))
        print(type(hotel_offers.data[0]))
        print(len(hotel_offers.data))
        for hotel in hotel_offers.data:
            print(hotel)


        num_hotels = len(hotel_offers.data)
        if num_hotels >= 5:
            hotels_to_display = hotel_offers.data[0:5]
        elif num_hotels < 5 and num_hotels > 0:
            hotels_to_display = hotel_offers.data[0:num_hotels]
        else:
            hotels_to_display = "No hotels found that match the search criteria."

        # print("\nHotels to display:")
        # print(type(hotels_to_display))
        # print(type(hotels_to_display[0]))
        # print(len(hotels_to_display))
        # print()

        # print(hotels_to_display)
        # print()

        output = ["Hotels:"]
        output.append(f"Check In Date: {hotels_to_display[0].get("offers")[0].get("checkInDate")}") # type: ignore
        output.append(f"Check Out Date: {hotels_to_display[0].get("offers")[0].get("checkOutDate")}") # type: ignore

        guests_info = "Guests: "
        for key in hotels_to_display[0].get("offers")[0].get("guests"): # type: ignore
            guests_info += f"{key}: {hotels_to_display[0].get("offers")[0].get("guests").get(key)}  " # type: ignore
        output.append(guests_info)

                  
        for hotel in hotels_to_display:
            output.append("")
            output.append("")
            for key in hotel:
                if key == "hotel":
                    output.append(f"Hotel Name : {hotel.get(key).get("name")}") # type: ignore

                elif key == "available":
                    output.append(f"Available : {hotel.get(key)}") # type: ignore

                elif key == "offers":
                    for offer in hotel.get(key): # type: ignore
                        output.append("")
                        output.append(f"Room Type: {offer.get("room").get("typeEstimated").get("category")}")
                        output.append(f"Beds: {offer.get("room").get("typeEstimated").get("beds")} {offer.get("room").get("typeEstimated").get("bedType")}")
                        output.append(f"Price: {offer.get("price").get("currency")} base: ${offer.get("price").get("base")} total: ${offer.get("price").get("total")}")
                        output.append(f"Average Price per night ${offer.get("price").get("variations").get("average").get("base")}")
                        output.append(f"Description: {offer.get("room").get("description").get("text")}")

        output_string = ""                  
        for line in output:
            print(line)
            output_string += str(line) + "  \n"

        print("\n\nOutput String:")
        print(output_string)

        self.hotel_info = str(output_string)



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
        print("--Running call_llm.")

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
            model=self.LLM_model,
            messages=self.chat_history, # type: ignore
        )

        return completion.choices[0].message.content
    

    def return_results(self):
        print("Running return results")
        return "\n\n" + str(self.flight_info) + str(self.hotel_info) + str(self.location_info)