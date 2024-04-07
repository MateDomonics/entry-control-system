from dataclasses import dataclass, field
from typing import Optional, Union
from uuid import uuid4
from api import Api
from os import path

@dataclass()
class User:
    uuid: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    active_subscription: bool
    #https://stackoverflow.com/questions/68874635/why-is-my-python-dataclass-not-initialising-boolean-correctly
    inside_facility: Optional[bool] = field(default=False)

    def __str__(self) -> str:
        return f"uuid: {self.uuid}, is inside: {self.inside_facility}"

    
class User_manager:
    def __init__(self, api_key: str) -> None:
        self.client = Api(api_key)
        self.table_name = "KapU_DB"

    @staticmethod
    def load_access(file_path: str) -> "User_manager":
        if not path.exists(file_path):
            raise FileNotFoundError("Couldn't create User Manager. File not found.")
        with open(file_path, "r") as fp:
            data = fp.read(-1).split("\n")
            return User_manager(api_key=data[0])

    def create_user(self) -> Union[User, None]:
        first_name = input("Please enter the customer's First Name: ")
        last_name = input("Please enter the customer's Last Name: ")
        email = input("Please enter the customer's email: ")
        phone_number = input("Please enter the customer's Phone Number: ")
        #UUID generates a UUID object, which is then converted into a hexadecimal number.
        user = User(uuid4().hex, first_name, last_name, email, phone_number, active_subscription=True)
        print(f"User Created: {user}")
        if self.save_user(user):
            return user
        print("User creation failed")
        return None
        

    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
    def save_user(self, user: User) -> bool:
        return self.client.create_user({
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
        })

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
    
    def get_user(self, uuid: str) -> Union[User, None]:
        response = self.client.get_user_by_id(uuid)
        print(response)
        if "Items" not in response or len(response["Items"]) != 1:
            return None
        usable_response = response["Items"][0]
        return User(usable_response["uuid"], usable_response["first_name"],
                    usable_response["last_name"], usable_response["email"], 
                    usable_response["phone_number"], usable_response["active_subscription"],
                    usable_response["inside_facility"])