from dataclasses import dataclass, field
from typing import Optional, Union
from uuid import uuid4
import boto3
from os import path

@dataclass()
class User():
    uuid: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    active_subscription: bool
    #https://stackoverflow.com/questions/68874635/why-is-my-python-dataclass-not-initialising-boolean-correctly
    inside_facility: Optional[bool] = field(default=False)

    
class User_manager():
    def __init__(self, aws_ak_id: str , aws_sak: str) -> None:
        #https://stackoverflow.com/questions/48645867/how-to-establish-a-connection-to-dynamodb-using-python-using-boto3
        self.client = boto3.client('dynamodb', aws_access_key_id=aws_ak_id, aws_secret_access_key=aws_sak, region_name= 'eu-west-1')
        self.table_name = "KapU_DB"

    @staticmethod
    def load_access(file_path: str) -> "User_manager":
        if not path.exists(file_path):
            raise FileNotFoundError("Couldn't create User Manager. File not found.")
        with open(file_path, "r") as fp:
            data = fp.read(-1).split("\n")
            if len(data) < 2:
                raise Exception("Couldn't create User Manager. Wrong file format/content.")
            return User_manager(aws_ak_id=data[0], aws_sak=data[1])

    def create_user(self) -> User:
        first_name = input("Please enter the customer's First Name: ")
        last_name = input("Please enter the customer's Last Name: ")
        email = input("Please enter the customer's email: ")
        phone_number = input("Please enter the customer's Phone Number: ")
        #UUID generates a UUID object, which is then converted into a hexadecimal number.
        user = User(uuid4().hex, first_name, last_name, email, phone_number, active_subscription=True)
        self.save_user(user)
        return user

    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
    def save_user(self, user: User) -> None:
        response = self.client.put_item(
            TableName = self.table_name,
            Item = {
                "uuid": {
                    "S": user.uuid
                },
                "first_name": {
                    "S": user.first_name
                },
                "last_name": {
                    "S": user.last_name
                },
                "email": {
                    "S": user.email
                },
                "phone_number": {
                    "S": user.phone_number
                },
                "active_subscription": {
                    "BOOL": user.active_subscription
                },
                "inside_facility": {
                    "BOOL": user.inside_facility
                }
            }
        )
        print(response)

    def update_user_presence(self, user: User) -> None:
        response = self.client.update_item(
            TableName = self.table_name,
            Key = {
                "uuid": {
                    "S": user.uuid
                },
            },
            UpdateExpression = f"SET #inside_facility = :{user.inside_facility}"
        )
        print(response)
    
    def get_user(self, uuid: str) -> Union[User, None]:
        response = self.client.get_item(
            TableName = self.table_name,
            Key = {
                "uuid": {
                    "S": uuid
                },
            },
        )
        if "Item" not in response:
            return None
        usable_response = response["Item"]
        return User(usable_response["uuid"]["S"], usable_response["first_name"]["S"],
                    usable_response["last_name"]["S"], usable_response["email"]["S"],
                    usable_response["phone_number"]["S"], usable_response["active_subscription"]["BOOL"],
                    usable_response["inside_facility"]["BOOL"])