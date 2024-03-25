from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import generic_helper
import mysql.connector

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
        'Calculate': calculate,
        'Car_or_Bike': calculate_for_car_or_bike,
        'After_User_Name':add_name,
        'Confirmation': check,
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
        # If the user exists, send a welcome back message
        return JSONResponse(content={"fulfillmentText": f"Hai welcome back {username}"})
    else:
        # If the user doesn't exist, create a new entry and send a welcome message
        with mydb.cursor() as cursor:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            cursor.execute("INSERT INTO user_carbon_footprints (username, carbon_footprint, entry_date) VALUES (%s, %s, CURDATE())", (username, 0.0))
            mydb.commit()
        return JSONResponse(content={"fulfillmentText": f"It's a pleasure to meet a new friend in my community. Welcome {username}"})