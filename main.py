from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import generic_helper
import mysql.connector
import random
import requests

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mahesh",
    database="environment"
)
# Carbon emission factors (in kgCO2 per km) for different transport modes
inprogress_orders={}

carbon_emission_factors = {
    "Car": 0.2,  # Example value, replace with actual data
    "Bus": 0.1,  # Example value, replace with actual data
    "Train": 0.05,
    "Bike": 0.3,
}

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    
    payload= await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    intent_handler_dict = {
        'Calculate--Calculate': calculate,
        'Car_or_Bike--Calculate': calculate_for_car_or_bike,
        'After_User_Name':add_name,
        'Confirmation for Calculate': check,
        'News':news,
        'Weather_News':weather,
    }

    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])
    return intent_handler_dict[intent](parameters,session_id)

def check(parameters:dict , session_id: str):
    if session_id not in inprogress_orders:
         return JSONResponse(content={
        "fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."
    })

def calculate(parameters: dict,session_id: str):

    print(session_id)
    if session_id not in inprogress_orders:
         return JSONResponse(content={
        "fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."
    })

    else:
        Distance = int(parameters["Distance"])
        TransportMode = parameters["TransportMode"].capitalize()
        carbon_emission = Distance * carbon_emission_factors.get(TransportMode, 0)
        username = inprogress_orders[session_id]
        cursor = mydb.cursor()
        cursor.execute("UPDATE user_carbon_footprints SET carbon_footprint = %s,entry_date =CURDATE()  WHERE username = %s",
                           (carbon_emission, username))
        mydb.commit()
        cursor.close()
        
        return JSONResponse(content={
            "fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {TransportMode} is {carbon_emission:.2f} kgCO2."
        })

def calculate_for_car_or_bike(parameters : dict,session_id: str):

    print(session_id)
    if session_id not in inprogress_orders:
         return JSONResponse(content={
        "fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."
    })

    else:
        Distance = int(parameters["Distance"])
        Car_Bike = parameters["Car_Bike"].capitalize()
        fuel_efficiency = int(parameters["Efficiency"])
        
    carbon_emission = Distance * (1 / fuel_efficiency)
    username = inprogress_orders[session_id]

    with mydb.cursor() as cursor:
        cursor.execute("UPDATE user_carbon_footprints SET carbon_footprint = %s,entry_date =CURDATE()  WHERE username = %s",
                           (carbon_emission, username))
        mydb.commit()
        cursor.close()
    
    return JSONResponse(content={
        "fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {Car_Bike} with an efficiency of {fuel_efficiency} km/l is {carbon_emission:.2f} kgCO2."
    })


def add_name(parameters: dict,session_id: str):

    username = parameters["Name"]['name']
    print(session_id)
    print("----------------")
    print(username)
    print("----------------")
    if session_id not in inprogress_orders:
        inprogress_orders[session_id]=username
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM user_carbon_footprints WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    print(existing_user)

    if existing_user:
        welcome_messages = [
            "Hey there {name}, what's on the agenda?",
            "Hi, {name} any plans for now?",
            "Hello {name}! What's next on our list?",
            "Hi {name}! Ready for our next step? "
        ]
        
        # Selecting a random welcome message
        selected_message = random.choice(welcome_messages)
        
        selected_message += "\n"
    
    # Concatenating the common static text with the selected message
        full_message = f"{selected_message}Shall I calculate the carbon footprint or Do you need recycling guidelines for some material or Latest Science News"
        # Formatting the selected message with the username
        formatted_message = full_message.format(name=username)
        
        # Returning the JSON response
        return JSONResponse(content={"fulfillmentText": formatted_message})
    else:
        # If the user doesn't exist, create a new entry and send a welcome message
        with mydb.cursor() as cursor:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            cursor.execute("INSERT INTO user_carbon_footprints (username, carbon_footprint, entry_date) VALUES (%s, %s, CURDATE())", (username, 0.0))
            mydb.commit()
        return JSONResponse(content={"fulfillmentText": f"It's a pleasure to meet a new friend in my community. Welcome {username} Shall we calculate the carbon footprint or Do you need recycling guidelines for some material."})
    
def news(parameters: dict,session_id: str):
    api_key = 'c9635a15c4a64806b169099b2816fb04'
    country = 'in'
    category = 'science'
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': country,
        'category': category,
        'apiKey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'ok':
        articles = data['articles']
        news_items = [article['title'] for article in articles]
        
        random_news = random.choice(news_items)
        return JSONResponse(content={"fulfillmentText": random_news})
    else:
        error_message = data.get('message', 'Unknown error')
        return JSONResponse(content={"fulfillmentText": f"Error fetching news: {error_message}"})
    
def weather(parameters: dict,session_id: str):
        # Replace 'YOUR_API_KEY' with your actual WeatherAPI key
    API_KEY = '3f14ccd416ab4d7cb80163732242503'
    BASE_URL = 'https://api.weatherapi.com/v1/current.json'

    # Specify the location for which you want to fetch weather data
    if(parameters['geo-state']):
        location = parameters['geo-state']
    else:
        location = parameters['geo-city']

    # Make the API request
    params = {
        'key': API_KEY,
        'q': location
    }
    response = requests.get(BASE_URL, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        # Extract relevant information from the response
        location_name = data['location']['name']
        current_temp_c = data['current']['temp_c']
        condition = data['current']['condition']['text']
        return JSONResponse({"fulfillmentText": f"The current temperature in {location_name} is around {current_temp_c}°C, and the condition is {condition}."})
        
    else:
       return JSONResponse({f'Error fetching weather data: {response.status_code}'})
