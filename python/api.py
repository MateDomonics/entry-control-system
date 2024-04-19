from typing import List, Dict, Any
import requests
import json
endpoint_url = "https://fl5loc5z14.execute-api.eu-west-1.amazonaws.com/Test"

"""
Builds GET, PUT and POST requests that are sent to the API Gateway Endpoint on AWS.
"""
class Api:

    """
    Initialize the class with the API Key that is gained from a secret file.
    """
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
    
    """
    GET all the users from the database and decode the returned JSON string into a dictionary.
    """
    def get_user_ids(self) -> List[str]:
        response = requests.get(endpoint_url, headers={"x-api-key":self.api_key})
        return json.loads(response.text)
    
    """
    PUT a new user onto the database using a payload that is a JSON string formed from a dictionary.
    """
    def create_user(self, payload: Dict[str, Any]) -> bool:
        payload = json.dumps(payload)
        response = requests.put(endpoint_url, payload, headers={"x-api-key":self.api_key})
        return response.status_code == 200 
    
    """
    GET a user based on their UUID and decode the returned JSON string into a dictionary.
    """
    def get_user_by_id(self, uuid: str) -> Dict[str, Any]:
        response = requests.get("/".join([endpoint_url, uuid]), headers={"x-api-key":self.api_key})
        return json.loads(response.text)

    """
    POST an updated user to the database using a payload that is a JSON string formed from a dictionary.
    """
    def update_user(self, uuid: str, payload: Dict[str, Any]) -> bool:
        payload = json.dumps(payload)
        response = requests.post("/".join([endpoint_url, uuid]), payload, headers={"x-api-key":self.api_key})
        return response.status_code == 200 

