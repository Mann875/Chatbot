from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

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
        return JSONResponse(content = {
            "fulfillmentText": f"Received == {intent} == in the backend"
        })
