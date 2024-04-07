from typing import List, Dict, Any
import requests
import json
endpoint_url = "https://fl5loc5z14.execute-api.eu-west-1.amazonaws.com/Test"

class Api:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        print(api_key)
    
    def get_user_ids(self) -> List[str]:
        response = requests.get(endpoint_url, headers={"x-api-key":self.api_key})
        print(f"GET user IDs: {response.status_code}, {response.reason}\n{response.text}")
        return json.loads(response.text)
    
    def create_user(self, payload: Dict[str, Any]) -> bool:
        payload = json.dumps(payload)
        print(payload)
        response = requests.put(endpoint_url, payload, headers={"x-api-key":self.api_key})
        print(f"PUT new user: {response.status_code}, {response.reason}\n{response.text}")
        return response.status_code == 200 
    
    def get_user_by_id(self, uuid: str) -> Dict[str, Any]:
        response = requests.get("/".join([endpoint_url, uuid]), headers={"x-api-key":self.api_key})
        print(f"GET user by ID: {response.status_code}, {response.reason} \n{response.text}")
        return json.loads(response.reason)

    def update_user(self, uuid: str, payload: Dict[str, Any]) -> bool:
        payload = json.dumps(payload)
        print(payload)
        response = requests.post("/".join([endpoint_url, uuid]), payload, headers={"x-api-key":self.api_key})
        print(f"POST update user: {response.status_code}, {response.reason}\n{response.text}")
        return response.status_code == 200 

