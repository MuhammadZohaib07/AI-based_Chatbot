from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])


    if intent == 'new.order':
        inprogress_orders.pop(session_id, None)
        fulfillment_text = "Starting a new order. Specify food items and quantities. For example, you can say: I would like to order two cookie doughs and one milkshake. Also, we have only the following items in our menu: cookie dough, waffle, milkshake, and doughnut."
        return JSONResponse(content={"fulfillmentText": fulfillment_text})


    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters, session_id)
    else:
        return JSONResponse(content={"fulfillmentText": "Sorry, I didn't understand that."})


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1
    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id


def complete_order(parameters: dict, session_id: str):
    fulfillment_text = ""
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please place a new order again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your order. Your order id is #{order_id}. Your order total is {order_total} which you can pay at the time of delivery! Would you like to give us rating based on our conversation from 1 to 5?"
        del inprogress_orders[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def add_to_order(parameters: dict, session_id: str):
    fulfillment_text = ""
    food_items = parameters["food-item"]
    quantities = [int(q) for q in parameters["number"]]
    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            for item, qty in new_food_dict.items():
                # If the item is already in the order, increment by the new quantity, otherwise add the new item
                if item in current_food_dict:
                    current_food_dict[item] += qty
                else:
                    current_food_dict[item] = qty
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def remove_from_order(parameters: dict, session_id: str):
    fulfillment_text = ""
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
    else:
        food_items = parameters["food-item"]
        quantities = [int(q) for q in parameters["number"]]
        current_order = inprogress_orders[session_id]
        removed_items = []
        no_such_items = []
        quantity_not_matched_items = []

        for item, quantity_to_remove in zip(food_items, quantities):
            if item in current_order:
                current_quantity = current_order[item]
                if quantity_to_remove < current_quantity:
                    current_order[item] = current_quantity - quantity_to_remove
                    removed_items.append(f"{quantity_to_remove} {item}(s)")
                elif quantity_to_remove == current_quantity:
                    del current_order[item]
                    removed_items.append(f"All {item}(s)")
                else:
                    quantity_not_matched_items.append(item)
            else:
                no_such_items.append(item)

        if removed_items:
            fulfillment_text = f'Removed {", ".join(removed_items)} from your order. '
        if no_such_items:
            fulfillment_text += f'No such items {", ".join(no_such_items)} found in your order. '
        if quantity_not_matched_items:
            fulfillment_text += f'The quantity specified for {", ".join(quantity_not_matched_items)} exceeds the quantity in your order. '

        if current_order:
            order_str = generic_helper.get_str_from_food_dict(current_order)
            fulfillment_text += f"Here's what's left in your order: {order_str}"
        else:
            fulfillment_text += "Your order is now empty!"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def track_order(parameters: dict, session_id: str):
    fulfillment_text = ""
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}."
    else:
        fulfillment_text = f"No order found with order id: {order_id}."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})
