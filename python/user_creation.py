from typing import Union
from uuid import uuid4
from api import Api
from datetime import datetime, timedelta
from time import mktime
from user import User
    
class User_manager:
    """
    Initalize the class with the API key that we use in the API class (refer to "api.py") and hard-code the DynamoDB table name.
    """
    def __init__(self, api: Api) -> None:
        self.client = api
        self.table_name = "KapU_DB"

    """
    CHANGE LATER
    Generate a User from user input, including a unique user identifier, then save the user to DynamoDB.
    Since saving the user could fail, I made sure to catch this error and either return the User or None (Union).
    """
    def configure_user(self) -> User:
        first_name = input("Please enter the customer's First Name: ")
        last_name = input("Please enter the customer's Last Name: ")
        email = input("Please enter the customer's email: ")
        phone_number = input("Please enter the customer's Phone Number: ")
        
        sub_length = None
        while sub_length is None:
            try:
                sub_length = int(input("Please enter the customer's subscription plan [Inputted value is considered in number of months]: "))
            except ValueError:
                print("Please only input a number for the subscription length.")

        # Take the current date, add the amount of months inputted above, and then turn it into a timestamp.
        end_of_sub = mktime((datetime.now().date() + timedelta(days=(sub_length*30))).timetuple())
        print(f"Subscription will expire at: {datetime.fromtimestamp(end_of_sub)}")
        
        #UUID generates a UUID object, which is then converted into a hexadecimal number.
        user = User(uuid4().hex, first_name, last_name, email, phone_number, end_of_sub)
        print(f"User Created: {user}")
        return user
        
    """
    Save the created User to DynamoDB via the API class.
    """
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
    def save_user(self, user: User) -> bool:
        return self.client.create_user(
            {
                "TableName": self.table_name,
                "Item": {
                    "uuid": user.uuid,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "active_subscription": user.active_subscription,
                    "inside_facility": user.inside_facility
                }
            }
        )

    """
    Update the presence of the User on DynamoDB if they entered or left the facility.
    """
    def update_user_presence(self, user: User) -> bool:
        return self.client.update_user(
            user.uuid,
            {
                "TableName": self.table_name,
                "Key": {"uuid": user.uuid},
                "UpdateExpression": "SET inside_facility = :if",
                "ExpressionAttributeValues": {":if": user.inside_facility}
            }
        )
    
    """
    Get the specific User from DynamoDB based on their UUID. 
    """
    def get_user(self, uuid: str) -> Union[User, None]:
        response = self.client.get_user_by_id(uuid)
        if "Items" not in response or len(response["Items"]) != 1:
            return None
        usable_response = response["Items"][0]
        return User(usable_response["uuid"], usable_response["first_name"],
                    usable_response["last_name"], usable_response["email"], 
                    usable_response["phone_number"], usable_response["active_subscription"],
                    usable_response["inside_facility"])