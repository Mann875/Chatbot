from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse


import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

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

    # It is used to get session id from the output context of the dialogflow
    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    # if intent == "track.order":
    #     response = track_order(parameters)
    #     return response
    # elif intent == "order.add - context: ongoing-order":
    #      pass
    # elif intent == "order.complete - context: ongoing-order":
    #      pass
    
    # Instead of above code a dictionary will be better option

    intent_handler_dict = {
      'order.add - context: ongoing-order': add_to_order,
      'order.remove - context: ongoing-order': remove_from_order,
      'order.complete - context: ongoing-order': complete_order,
      'track.order - context: ongoing-order': track_order,
    } 

    return intent_handler_dict[intent](parameters, session_id)



def remove_from_order(parameters: dict, session_id: str):
    #  First we need to find its sesssion id
    # Secondly we have to get values from dict
    # And at last remove the food items
    
    if session_id not in inprogress_orders:
         return JSONResponse(content={
              "fulfillmentText": "Trouble in finding your order, Kindly start new order again!"
         })
    
    current_order = inprogress_orders[session_id]
    food_items = parameters["food-item"]

    removed_items = []
    no_such_items = []

    for item in food_items:
         if item not in current_order:
              no_such_items.append(item)
         else:
              removed_items.append(item)
              del current_order[item]
         
    # Message to user about removed items
    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items):
        fulfillment_text = f'your current order does not have {",".join(no_such_items)}'      

    if len(current_order) == 0:
        fulfillment_text = "Your order is empty!"
    else:
        order_str =  generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text = f"Here is what is left in your order: {order_str}"
    
    return JSONResponse(content={
         "fulfillmentText": fulfillment_text
    })
    
         


def add_to_order(parameters:dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I did't understant. Can you please specify food items and quantities"

    else:
         new_food_dict = dict(zip(food_items, quantities))


        #  dict for food order, for new order create new dict and for current order, just add food item
         if session_id in inprogress_orders:
              current_food_dict = inprogress_orders[session_id]
              current_food_dict.update(new_food_dict)
              inprogress_orders[session_id] = current_food_dict
         else:
              inprogress_orders[session_id] = new_food_dict
              
         order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
         fulfillment_text = f"Now you have: {order_str} in your order. Do you need anything else?"

    return JSONResponse(content={
         "fulfillmentText": fulfillment_text
    })

'''
There might be multiple user using the chat bot at the same time
and after add order there is also an option to add again,
in that to make sure that the order gets added to the same order id

Session must be used
There is already a session id attached to each conversations in the dialogflow
'''

def complete_order(parameters: dict, session_id: str):
     if session_id not in inprogress_orders:
          fulfillment_text = "There is a trouble in finding your order. You will have to place new order again. "
     else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
             fulfillment_text = "Sorry, I couldn't process your error due to a backend error." \
                  "Please place new order again"

        else:
             order_total = db_helper.get_total_order_price(order_id)
             fulfillment_text = f"Your Order has been placed Successfully!" \
             f"Here is your order id #{order_id}." \
             f"Your order total is {order_total}. You have to pay this at the time of delivery!"
        

        del inprogress_orders[session_id]


     return JSONResponse(content={
        "fulfillmentText": fulfillment_text 
    })




def save_to_db(order: dict):

    next_order_id = db_helper.get_next_order_id()
    #  To save the order, Assign the order id the number which is +1 than the max order id that already exists 
    for food_item, quantity in order.items():
          rcode = db_helper.insert_order_item(
               food_item,
               quantity,
               next_order_id
          )
          
          if rcode == -1:
               return -1
    
    
    db_helper.insert_order_tracking(next_order_id, "in progress")
    
    return next_order_id



def track_order(parameters: dict, session_id: str):
        order_id = int(parameters['order_id'])
        order_status = db_helper.get_order_status(order_id)

        if order_status:
            fulfillment_text = f"The order status for order id {order_id} is: {order_status}"
        else:
            fulfillment_text = f"No order found with order id: {order_id}"
              
              
        return JSONResponse(content = {
            "fulfillmentText": fulfillment_text
        })

