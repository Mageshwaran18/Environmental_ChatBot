from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import generic_helper

# Carbon emission factors (in kgCO2 per km) for different transport modes
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
    }

    return intent_handler_dict[intent](parameters)

def calculate(parameters: dict):

    Distance = int(parameters["Distance"])
    TransportMode = parameters["TransportMode"].capitalize()
    carbon_emission = Distance * carbon_emission_factors.get(TransportMode, 0)
    
    return JSONResponse(content={
        "fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {TransportMode} is {carbon_emission:.2f} kgCO2."
    })

def calculate_for_car_or_bike(parameters : dict):

    Distance = int(parameters["Distance"])
    Car_Bike = parameters["Car_Bike"].capitalize()
    fuel_efficiency = int(parameters["Efficiency"])
    
    carbon_emission = Distance * (1 / fuel_efficiency)
    
    return JSONResponse(content={
        "fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {Car_Bike} with an efficiency of {fuel_efficiency} km/l is {carbon_emission:.2f} kgCO2."
    })
