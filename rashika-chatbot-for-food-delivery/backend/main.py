from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

# Dictionary to store in-progress orders by session ID
inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    # Mapping intents to corresponding handler functions
    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    # Using .get() to avoid KeyError if intent is not found
    handler = intent_handler_dict.get(intent)
    if handler:
        return handler(parameters, session_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid intent")  # Return error if intent is not valid


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    # Insert individual items along with quantity in orders table
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)

        if rcode == -1:
            return -1  # Early exit if an error occurs

    # Now insert order tracking status
    db_helper.insert_order_tracking(next_order_id, "in progress")

    return next_order_id


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        # Modified response for clarity
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please place a new order again"
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your order. Here is your order id # {order_id}. Your order total is {order_total} which you can pay at the time of delivery!"

        del inprogress_orders[session_id]  # Clear the order after completion

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        # Update or initialize the in-progress order for the session
        inprogress_orders.setdefault(session_id, {}).update(new_food_dict)

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={"fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order please?"})

    food_items = parameters.get("food-item", [])
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    # Building the response text based on removed and missing items
    fulfillment_text = ""
    if removed_items:
        fulfillment_text += f'Removed {", ".join(removed_items)} from your order! '
    if no_such_items:
        fulfillment_text += f'Your current order does not have {", ".join(no_such_items)}. '
    if not current_order:
        fulfillment_text += "Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Here is what is left in your order: {order_str}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

# Note: Ensure to add appropriate error handling for database operations
