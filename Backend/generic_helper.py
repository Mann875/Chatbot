import re

def extract_session_id(session_str: str):

    match = re.search(r"/sessions/(.*?)/contexts", session_str)

    if match:
         extract_session_id = match.group(1)
         return extract_session_id

    return "" 

''' Now order is stored, The following function helps to display the order in the string format'''
def get_str_from_food_dict(food_dict: dict):
     return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])