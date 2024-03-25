from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

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
        'Calculate':calculate,
    }

    return intent_handler_dict[intent](parameters)

def calculate(parameters: dict):

    Distance = int(parameters["Distance"])
    TransportMode = parameters["TransportMode"].capitalize()
    carbon_emission = Distance * carbon_emission_factors.get(TransportMode)
    return JSONResponse(content={
        "fulfillmentText": f"Your carbon footprint for traveling {Distance} km by {TransportMode} is {carbon_emission} kgCO2."
    })

