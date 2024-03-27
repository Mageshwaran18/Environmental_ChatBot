from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import generic_helper
import mysql.connector
import random
import requests
from bs4 import BeautifulSoup
import time


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
        'Travell': travel,
        'Largest of Recycle': large,
        'SomeOther': some,
    }

    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])
    return intent_handler_dict[intent](parameters,session_id)

def check(parameters:dict , session_id: str):
    if session_id not in inprogress_orders:
         return JSONResponse(content={
        "fulfillmentText": "I think you forgot to enter the Name. Please enter the name to proceed."
    })

def some(parameters:dict , session_id: str):
    
    if session_id not in inprogress_orders:
         return JSONResponse(content={
        "fulfillmentText": f"Shall I calculate the carbon footprint or Do you need recycling guidelines for some material or Latest Science News or weather updates of your city or Shall I provide insights into the top company or organization worldwide that deals with recycling of Plastic,Glass,E waste or Do you need certain cities Air pollution level"
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
        """cursor = mydb.cursor()
        cursor.execute("UPDATE user_carbon_footprints SET carbon_footprint = %s,entry_date =CURDATE()  WHERE username = %s",
                           (carbon_emission, username))
        mydb.commit()
        cursor.close()"""
        
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

    """with mydb.cursor() as cursor:
        cursor.execute("UPDATE user_carbon_footprints SET carbon_footprint = %s,entry_date =CURDATE()  WHERE username = %s",
                           (carbon_emission, username))
        mydb.commit()
        cursor.close()"""
    
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
        full_message = f"{selected_message}Shall I calculate the carbon footprint or Do you need recycling guidelines for some material or Latest Science News or weather updates of your city or Shall I provide insights into the top company or organization worldwide that deals with recycling of Plastic,Glass,E waste or Do you need certain cities Air pollution level"
        # Formatting the selected message with the username
        formatted_message = full_message.format(name=username)
        
        # Returning the JSON response
        return JSONResponse(content={"fulfillmentText": formatted_message})
    else:
        # If the user doesn't exist, create a new entry and send a welcome message
        """with mydb.cursor() as cursor:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            cursor.execute("INSERT INTO user_carbon_footprints (username, carbon_footprint, entry_date) VALUES (%s, %s, CURDATE())", (username, 0.0))
            mydb.commit()"""
        return JSONResponse(content={"fulfillmentText": f"It's a pleasure to meet a new friend in my community. Welcome {username} Shall we calculate the carbon footprint or Do you need recycling guidelines for some material or Latest Science News or weather updates of your city or Shall I provide insights into the top company or organization worldwide that deals with recycling of Plastic,Glass,E waste or Do you need certain cities Air pollution level"})
    
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

def get_coordinates(city_name, api_key):
    # API endpoint for geocoding
    url = 'https://api.openweathermap.org/data/2.5/weather'

    # Parameters
    params = {
        'q': city_name,
        'appid': api_key
    }

    # Send GET request
    response = requests.get(url, params=params)

    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()
        # Extract latitude and longitude
        coord_lat = data['coord']['lat']
        coord_lon = data['coord']['lon']
        return coord_lat, coord_lon
    else:
        # Print error message if request failed
        print('Failed to fetch data:', response.status_code)
        return None, None

def get_pollution_level(aqi):
    if aqi == 1:
        return "Good"
    elif aqi == 2  :
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4 :
        return "poor"
    elif aqi==5:
      return "very poor"

    
"""def travel(parameters: dict, session_id: str):
    if 'geo-city' in parameters:
        city_name = parameters['geo-city']
    elif 'geo-state' in parameters:
        city_name = parameters['geo-state']
    else:
        return JSONResponse(content={"fulfillmentText": "Please provide a valid city name."})

    api_key_weather = '746575324d532010700d47a868e9a886'
    response_text = ""
    latitude, longitude = get_coordinates(city_name, api_key_weather)

    if latitude and longitude:
        weather_url = 'https://api.openweathermap.org/data/2.5/weather'
        weather_params = {
            'lat': latitude,
            'lon': longitude,
            'appid': api_key_weather
        }
        weather_response = requests.get(weather_url, params=weather_params)
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            current_temperature = weather_data['main']['temp']
            weather_description = weather_data['weather'][0]['description']
        else:
            response_text = "Failed to fetch weather data."
    else:
        response_text = "Failed to get coordinates for the city."

    if latitude and longitude:
        air_pollution_url = 'https://api.openweathermap.org/data/2.5/air_pollution'
        air_pollution_params = {
            'lat': latitude,
            'lon': longitude,
            'appid': api_key_weather
        }
        air_pollution_response = requests.get(air_pollution_url, params=air_pollution_params)
        print(air_pollution_response)
        if air_pollution_response.status_code == 200:
            air_pollution_data = air_pollution_response.json()
            aqi = air_pollution_data['list'][0]['main']['aqi']
            co = air_pollution_data['list'][0]['components']['co']
            no = air_pollution_data['list'][0]['components']['no']
            no2 = air_pollution_data['list'][0]['components']['no2']
            o3 = air_pollution_data['list'][0]['components']['o3']
            so2 = air_pollution_data['list'][0]['components']['so2']
            nh3 = air_pollution_data['list'][0]['components']['nh3']
            pollution_level = get_pollution_level(aqi)
            if pollution_level in ['poor', 'very poor']:
                response_text = f"The Air Quality Index (AQI) in {city_name} is {aqi}, indicating {pollution_level} air quality. It's advised not to visit the city due to poor air quality."
                
            response_text += f"The Air Quality Index (AQI) in {city_name} is {aqi}, indicating {pollution_level} air quality."
            response_text += f"Pollutant components:\n"
            response_text += f"- Carbon Monoxide (CO): {co} µg/m³\n"
            response_text += f"- Nitrogen Monoxide (NO): {no} µg/m³\n"
            response_text += f"- Nitrogen Dioxide (NO2): {no2} µg/m³\n"
            response_text += f"- Ozone (O3): {o3} µg/m³\n"
            response_text += f"- Sulfur Dioxide (SO2): {so2} µg/m³\n"
            response_text += f"- Ammonia (NH3): {nh3} µg/m³\n"
        else:
            response_text += "Failed to fetch air pollution data."
    else:
        response_text += "Failed to get coordinates for air pollution data."

    return JSONResponse(content={"fulfillmentText": response_text})"""

def travel(parameters: dict, session_id: str):
    state=parameters['state']
    city=parameters['geo-city']
    if city=='Bengaluru':
        city='Bangalore'
    print(state)
    print(city)
    # Define the URL of the webpage containing the air quality table
    url = f'https://www.aqi.in/in/dashboard/india/{state}/'

    def scrape_air_quality_data():
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the webpage using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table with class "state-table" and id "state-table"
            table = soup.find('table', {'class': 'table state-table', 'id': 'state-table'})

            if table:
                # Extract and display the table's content
                air_quality_data = []
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        air_quality_data.append(row_data)
                
                return air_quality_data
            else:
                return "Could not find the air quality table on the webpage."
        else:
            return "Failed to retrieve data from the webpage."

    # Run the scraping function
    def get_air_quality_for_city(city_name, air_quality_data):
    # Iterate through each row in air_quality_data
        for row in air_quality_data:
            # Check if the first element of the row matches the city_name
            if row[0] == city_name:
                return row  # Return the row if the city_name matches
        return None 
    air_quality_data = scrape_air_quality_data()
    air_quality_data = get_air_quality_for_city(city, air_quality_data)



    # Formatting the response
    print(air_quality_data)
    fulfillment_text = f"The air quality data for {city} is: Status: {air_quality_data[1]}"


    # Return the response as JSONResponse
    return JSONResponse({"fulfillmentText": fulfillment_text})



def large(parameters: dict, session_id: str):
    item = parameters.get('item').capitalize()
    print(item)

    if not item:
        return {"fulfillmentText": "Please specify an item."}

    url = 'https://www.epa.gov/smm/recycling-economic-information-rei-report'

    def scrape_and_display_data():
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

        return response_text
    
    response_text = scrape_and_display_data()


    return {"fulfillmentText": response_text}
