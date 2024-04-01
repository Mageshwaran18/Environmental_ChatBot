import asyncio
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import generic_helper
import random

app = FastAPI()

inprogress_orders = {}

carbon_emission_factors = {
    "Car": 0.2,  
    "Bus": 0.1,  
    "Train": 0.05,
    "Bike": 0.3,
}

class WebhookRequest(BaseModel):
    responseId: str
    queryResult: dict
    session: str

@app.post("/")
async def webhook(request: WebhookRequest):
    print(request.responseId)
    print(request.session)
    parameters = request.queryResult.get('parameters', {})
    intent = request.queryResult.get('intent', {}).get('displayName')
    session_id = generic_helper.extract_session_id(request.session)

    intent_handler_dict = {
        'Calculate--Calculate': calculate,
        'Car_or_Bike--Calculate': calculate_for_car_or_bike,
        'After_User_Name': add_name,
        'Confirmation for Calculate': check,
        'News': news,
        'Weather_News': weather,
        'Travell': travel,
        'Largest of Recycle': large,
        'SomeOther': some,
        'End':end,
    }

    return await intent_handler_dict.get(intent, some)(parameters, session_id)

async def end(parameters:dict , session_id: str):
    print(inprogress_orders[session_id])
    del inprogress_orders[session_id]

async def check(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return {"fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."}

async def some(parameters: dict, session_id: str):
    return {"fulfillmentText": "Then , Shall I calculate the carbon footprint or Do you need recycling guidelines for some material or Latest Science News or weather updates of your city or Shall I provide insights into the top company or organization worldwide that deals with recycling of Plastic,Glass,E waste or Do you need certain cities Air pollution level"}

async def calculate(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return {"fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."}

    Distance = int(parameters["Distance"])
    TransportMode = parameters["TransportMode"].capitalize()
    carbon_emission = Distance * carbon_emission_factors.get(TransportMode, 0)
    username = inprogress_orders[session_id]

    return {"fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {TransportMode} is {carbon_emission:.2f} kgCO2."}

async def calculate_for_car_or_bike(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return {"fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."}

    Distance = int(parameters["Distance"])
    Car_Bike = parameters["Car_Bike"].capitalize()
    fuel_efficiency = int(parameters["Efficiency"])

    carbon_emission = Distance * (1 / fuel_efficiency)

    return {"fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {Car_Bike} with an efficiency of {fuel_efficiency} km/l is {carbon_emission:.2f} kgCO2."}

async def add_name(parameters: dict, session_id: str):
    username = parameters["Name"].get('name')
    print(username)
    if session_id not in inprogress_orders:
        inprogress_orders[session_id] = username

    welcome_messages = [
        "Hey there {name}, what's on the agenda?",
        "Hi, {name} any plans for now?",
        "Hello {name}! What's next on our list?",
        "Hi {name}! Ready for our next step? "
    ]

    selected_message = random.choice(welcome_messages)
    selected_message += "\n"

    full_message = f"{selected_message}Shall I calculate the carbon footprint or Do you need recycling guidelines for some material or Latest Science News or weather updates of your city or Shall I provide insights into the top company or organization worldwide that deals with recycling of Plastic,Glass,E waste or Do you need certain cities Air pollution level"

    formatted_message = full_message.format(name=username)

    return {"fulfillmentText": formatted_message}

async def news(parameters: dict, session_id: str):
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
        return {"fulfillmentText": random_news}
    else:
        error_message = data.get('message', 'Unknown error')
        return {"fulfillmentText": f"Error fetching news: {error_message}"}

async def weather(parameters: dict, session_id: str):
    API_KEY = '3f14ccd416ab4d7cb80163732242503'
    BASE_URL = 'https://api.weatherapi.com/v1/current.json'

    location = parameters.get('geo-state') or parameters.get('geo-city')
    params = {
        'key': API_KEY,
        'q': location
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        location_name = data['location']['name']
        current_temp_c = data['current']['temp_c']
        condition = data['current']['condition']['text']
        return {"fulfillmentText": f"The current temperature in {location_name} is around {current_temp_c}°C, and the condition is {condition}."}
    else:
        return {"fulfillmentText": f"Error fetching weather data: {response.status_code}"}

async def travel(parameters: dict, session_id: str):
    state = parameters.get('state')
    city = parameters.get('geo-city', parameters.get('city'))
    print(state)
    print(city)

    if city is None:
        return {"fulfillmentText": "Please provide a valid city name."}

    url = f'https://www.aqi.in/in/dashboard/india/{state}/{city}'

    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_description = soup.find('meta', attrs={'name': 'twitter:description'})
        if meta_description:
            description_content = meta_description['content']
            print(description_content)
            return {"fulfillmentText": description_content}
    else:
        return {"fulfillmentText": f"Failed to fetch air quality data for {city}, {state}."}

async def large(parameters: dict, session_id: str):
    item = parameters.get('item').capitalize()

    if not item:
        return {"fulfillmentText": "Please specify an item."}

    url = 'https://www.epa.gov/smm/recycling-economic-information-rei-report'

    response_text = ""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table_1 = soup.find('caption', text='Recycling and Reuse Activities in 2012').find_parent('table')

        if table_1:
            response_text += "Recycling and Reuse Activities in 2012:\n"
            rows = table_1.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    response_text += f"{row_data[0]}: {row_data[1]} - {row_data[2]}\n"

        table_2_row = soup.find('th', text=item).find_parent('tr')
        if table_2_row:
            table_2_cells = table_2_row.find_all(['th', 'td'])
            table_2_data = [cell.get_text(strip=True) for cell in table_2_cells]
            if table_2_data:
                response_text += f"\nOrganizations associated with {item} Recycling:\n"
                for org in table_2_data[1].split('\n'):
                    response_text += f"- {org.strip()}\n"

    else:
        response_text = "Failed to retrieve data from the webpage."

    return {"fulfillmentText": response_text}
