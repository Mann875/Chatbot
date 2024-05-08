from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

import db_helper

app = FastAPI()

@app.get("/")
async def root():
    return {"message" : "Hello World"}

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    # It will get the data from the json file of chat bot from the dialogflow

    payload = await request.json()

    # After that get the information from the payload is such a way that
    # it is based on the format/structure of the webhookRequest from the Dialogflow

    intent = payload['queryResult']['intent']['displayname']
    parameters = payload['queryResult']['parameter']
    output_contexts = payload['queryResult']['outputContexts']

    if intent == "track.order":
            track_order(parameters)


def track_order(parameters: dict):
        order_id = parameters['order_id']
        order_status = db_helper.get_order_status(order_id)

        if order_status:
            fulfillment_text = f"The order status for order id {order_id} is: {order_status}"
        else:
            fulfillment_text = f"No order found with order id: {order_id}"
              
              
        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text
        })

