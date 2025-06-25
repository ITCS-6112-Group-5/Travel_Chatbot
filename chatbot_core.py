# Shared Chatbot logic for both Streamlit App and Website Dev


import os
import json
from datetime import date
from amadeus import Client, ResponseError # Hotels API
from fast_flights import FlightData, Passengers, Result, get_flights # Flights API
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


# Chatbot --------------------------------------------------------------------------------

class Chatbot():
    def __init__(self):
        self.input_prompt = ""
        self.todays_date = date.today().isoformat()

        self.LLM_model = "llama-3.3-70b-versatile"

        self.amadeus = Client(
            client_id = os.getenv("AMADEUS_API_KEY"),
            client_secret = os.getenv("AMADEUS_API_SECRET")
        )

        # chat_history to store all of the messages in the conversation.
        # Set the system prompt to establish the behavior of the chatbot.
        self.chat_history = [
                                {"role": "system", 
                                "content": "You are a travel assistant named NaviBlu who helps provide information to users for planning trips and vacations."}
                            ]
        # seperate history to store just the user's messages
        self.user_message_history = []

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

        # Reset info
        self.flight_info = ""
        self.hotel_info = ""
        self.location_info = ""
        self.general_info = ""

        # Add to chat history
        self.chat_history.append({"role": "user", "content": str(self.input_prompt)})
        self.user_message_history.append({"role": "user", "content": str(self.input_prompt)})
        
        # make seperate chat history just for this process
        process_input_history = [{
                                    "role": "system", 
                                    "content": """You are an AI assistant tasked with determining if the user's most recent prompt is looking for the categories of 'flight', 'hotel', 'location', or 'general' information.
                                                If a category has already been used in an earlier assistant message and the most recent user message does not require it to be run again, do not run it again!! Just return the category they are currently looking for.
                                                Return only the names of the categories the prompt is asking about, 'flight', 'hotel', 'location', or 'general'. Only include 'location' if the user is asking for information about attractions and activities at a location.
                                                
                                                Here are some examples to follow:
                                                user: can you find flights to New York?
                                                assistant: flight

                                                user: can you find hotels in vancouver this weekend?
                                                assistant: hotel

                                                user: what are hotels near popular tourist locations in Orlando?
                                                assistant: hotel, location

                                                user: help me plan an entire trip from Charlotte to London this weekend.
                                                assistant: flight, hotel, location

                                                user: what are some popular activities to do in Wellington, New Zealand?
                                                assistant: location

                                                user: How far is Tokyo from New York?
                                                assistant: general
                                                """
                                }]
        
        # Add all of the user's messages to process_input_history
        for message in self.chat_history:
            process_input_history.append(message)


        completion = self.client.chat.completions.create(
            model = self.LLM_model,
            messages = process_input_history, # type: ignore
            temperature = 0.1
        )

        categories = str(completion.choices[0].message.content)
        print(f"---User Query Categories: {categories}---")
        self.user_message_history.append({"role": "assistant", "content": str(categories)}) # Add what agents were called for each query

        if ("flight" in categories):
            self.flight_info = self.flight_agent()

        if ("hotel" in categories):
            self.hotel_info = self.hotel_agent()

        if ("location" in categories):
            self.location_info = self.location_agent()

        if ("general" in categories):
            self.general_info = self.general_info_agent()
        

        # Combine the responses of all the agents
        assistant_response = f"{self.flight_info}\n + {self.hotel_info}\n + {self.location_info}\n + {self.general_info}"

        # Add AI response to chat history
        self.chat_history.append({"role": "assistant", "content": assistant_response})

        print("Outputing Message.\n")
        return assistant_response
    




    def flight_agent(self):
        """Uses an LLM to parse flight parameters the user is searching for. Then uses an API to search for available flights."""
        print("Running flight agent.")

        flight_info_prompt = f"""Use this user message history to extract the flight information the user is currently looking for: 
                user message history: {self.user_message_history}
                format your response as a json exactly structured like below and nothing else. If you can't find information for a section, make an educated guess based on the message history. 
                If needed, today's date is {self.todays_date}.

                {{
                "tripType": either "round-trip" or "one-way",
                "originCity": three letter origin city iataCode,
                "destinationCity": three letter destination city iataCode,
                "originAirport": three letter origin airport code based on the city,
                "destinationAirport": three letter destination airport code based on the city,
                "departureDate": "YYY-MM-DD",
                "arrivalDate": "YYY-MM-DD" if tripType is one-way, enter "None" for this field,
                "numAdults": X If no number is specified, assume 2,
                "numChildren": X If no number is specified, assume 0,
                "seat": either "economy", "premium-economy", "business", or "first". If no specification is made, enter "economy"
                }}
                """
        
        # Use LLM to parse flight search parameters from prompt
        search_info = self.call_llm(prompt = flight_info_prompt)
        # convert to JSON
        search_info_json = json.loads(search_info) # type: ignore

        output = ["Flight Search Parameters:"]
        output.append("--------------------------------------------------------")
        output.append(f"Trip Type: {search_info_json.get("tripType")},   Seat Type: {search_info_json.get("seat")}")
        output.append(f"Origin City: {search_info_json.get("originCity")},   Destination City: {search_info_json.get("destinationCity")}")
        output.append(f"Origin Airport: {search_info_json.get("originAirport")},   Destination Airport: {search_info_json.get("destinationAirport")}")
        if search_info_json.get("tripType") == "one-way":
            output.append(f"Departure: {search_info_json.get("departureDate")}")
        else:
            output.append(f"Departure: {search_info_json.get("departureDate")},   Arrival: {search_info_json.get("arrivalDate")}")
        output.append(f"Adults: {search_info_json.get("numAdults")},   Children: {search_info_json.get("numChildren")}\n")



        # get info for outbound flight 
        outbound: Result = get_flights(
            flight_data=[
                FlightData(date=search_info_json.get("departureDate"), from_airport=search_info_json.get("originAirport"), to_airport=search_info_json.get("destinationAirport"))
            ],
            trip="one-way",
            seat=search_info_json.get("seat"),
            passengers=Passengers(adults=search_info_json.get("numAdults"), children=search_info_json.get("numChildren"), infants_in_seat=0, infants_on_lap=0),
            fetch_mode="fallback",
        )

        output.append("Outbound Flights:-----------------------------------")
        output.append(f"Current Prices: {outbound.current_price}\n")

        for flight in outbound.flights:
            if flight.is_best == True:
                #print(f"Is best?: {flight.is_best}")
                output.append(f"Airline Name: {flight.name}")
                output.append(f"Departure: {flight.departure}")
                output.append(f"Arrival: {flight.arrival}")
                output.append(f"Duration: {flight.duration}")
                output.append(f"Stops: {flight.stops}")
                output.append(f"Price: {flight.price}")
                output.append("\n")


        # If round-trip, get info for inbound flight as well. (fast-flights API doesn't support normal round-trip)
        if search_info_json.get("tripType") == "round-trip":
            inbound: Result = get_flights(
                flight_data=[
                    FlightData(date=search_info_json.get("arrivalDate"), from_airport=search_info_json.get("destinationAirport"), to_airport=search_info_json.get("originAirport"))
                ],
                trip="one-way",
                seat=search_info_json.get("seat"),
                passengers=Passengers(adults=search_info_json.get("numAdults"), children=search_info_json.get("numChildren"), infants_in_seat=0, infants_on_lap=0),
                fetch_mode="fallback",
            )

            output.append("Inbound Flights:-----------------------------------")
            output.append(f"Current Prices: {inbound.current_price}\n")

            for flight in inbound.flights:
                if flight.is_best == True:
                    #print(f"Is best?: {flight.is_best}")
                    output.append(f"Airline Name: {flight.name}")
                    output.append(f"Departure: {flight.departure}")
                    output.append(f"Arrival: {flight.arrival}")
                    output.append(f"Duration: {flight.duration}")
                    output.append(f"Stops: {flight.stops}")
                    output.append(f"Price: {flight.price}")
                    output.append("\n")

                
        output_string = ""                  
        for line in output:
            output_string += str(line) + "  \n"

        print("\n\nFlight Output String:\n")
        print(output_string)

        return str(output_string)



    def hotel_agent(self):
        print("Running hotel agent.\n")

        prompt = f"""Use this user message history to extract the hotel information the user is currently looking for: 
                user message history: {self.user_message_history}
                format your response as a json exactly structured like below and nothing else. If you can't find information for a section, make an educated guess based on the message history. 
                If needed, today's date is {self.todays_date}.

                {{
                "city": three letter city iataCode,
                "checkInDate": "YYY-MM-DD",
                "checkOutDate": "YYY-MM-DD",
                "numGuests": X
                }}
                """
        
        search_info = self.call_llm(prompt = prompt)
        print(search_info)
        print()

        # convert to JSON
        search_info_json = json.loads(search_info) # type: ignore
        

        # Get list of hotels by city code
        hotel_response = self.amadeus.reference_data.locations.hotels.by_city.get(cityCode=search_info_json.get("city"))

        # Make list of hotel Ids
        hotel_ids = []
        for hotel in hotel_response.data:
            hotel_ids.append(str(hotel.get("hotelId")))
            #print(hotel)

        try:
            hotel_offers = self.amadeus.shopping.hotel_offers_search.get(
                hotelIds = hotel_ids[0:30], # search through first number of hotel ids
                checkInDate = search_info_json.get("checkInDate"),
                checkOutDate = search_info_json.get("checkOutDate"),
                adults = search_info_json.get("numGuests")
            )
            num_hotels = len(hotel_offers.data)
        except:
            return "Unable to find that match the search criteria."



        
        if num_hotels >= 5:
            hotels_to_display = hotel_offers.data[0:5]
        elif num_hotels < 5 and num_hotels > 0:
            hotels_to_display = hotel_offers.data[0:num_hotels]
        else:
            return "Unable to find that match the search criteria."
        

        output = ["\nHotel Search Parameters:"]
        output.append("--------------------------------------------------------")
        output.append(f"Check In Date: {hotels_to_display[0].get("offers")[0].get("checkInDate")}") # type: ignore
        output.append(f"Check Out Date: {hotels_to_display[0].get("offers")[0].get("checkOutDate")}") # type: ignore
        output.append(f"City: {search_info_json.get("city")}")

        guests_info = "Guests: "
        for key in hotels_to_display[0].get("offers")[0].get("guests"): # type: ignore
            guests_info += f"{key}: {hotels_to_display[0].get("offers")[0].get("guests").get(key)}  " # type: ignore
        output.append(guests_info)


        for hotel in hotels_to_display:
            try:
                output.append("")
                output.append("")
                for key in hotel:
                    if key == "hotel":
                        output.append(f"Hotel Name : {hotel.get(key).get("name")}") # type: ignore

                    elif key == "available":
                        output.append(f"Available : {hotel.get(key)}") # type: ignore

                    elif key == "offers":
                        for offer in hotel.get(key): # type: ignore
                            output.append(f"Room Type: {offer.get("room").get("typeEstimated").get("category")}")
                            output.append(f"Beds: {offer.get("room").get("typeEstimated").get("beds")} {offer.get("room").get("typeEstimated").get("bedType")}")
                            output.append(f"Price: {offer.get("price").get("currency")} base: ${offer.get("price").get("base")} total: ${offer.get("price").get("total")}")
                            output.append(f"Average Price per night ${offer.get("price").get("variations").get("average").get("base")}")
                            output.append(f"Description: {offer.get("room").get("description").get("text")}")
            except:
                print("Invalid Hotel Info")

        
        output.append("")
        output_string = ""                  
        for line in output:
            output_string += str(line) + "  \n"

        print("\n\nHotel Output String:")
        print(output_string)

        return str(output_string)



    def location_agent(self):
        print("Running location agent.")
        location_prompt = f"Use this user prompt to provide relevant information on the requested location including popular tourist attractions and activities: {self.input_prompt}"
        response = self.call_llm(prompt = location_prompt)
        print(response)
        print()
        return response



    def general_info_agent(self):
        print("Running general info agent.")
        general_prompt = f"Use this user prompt to provide relevant general information: {self.input_prompt}"
        return self.call_llm(prompt = general_prompt)





    def call_llm(self, prompt):
        """function for general purpose LLM calls."""
        print("--Running call_llm.")

        # make chat history to send to LLM
        history = [{
                    "role": "user",
                    "content": prompt,
                    }]

        # Call LLM
        completion = self.client.chat.completions.create(
            model = self.LLM_model,
            messages = history, # type: ignore
        )

        return completion.choices[0].message.content
    