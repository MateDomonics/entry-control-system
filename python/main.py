from scanner import Nfc
import requests
from hashlib import md5
import atexit
from os import path
from user_creation import User_manager

api = "https://eooorfidlkf4wow.m.pipedream.net"
#Key value pair where the key is the user's ID and the value shows whether they are present at the "venue" or not.
database = {}
nfc_reader:Nfc = None
user_manager = User_manager.load_access(path.join(path.dirname(path.dirname(__file__)), "aws_access"))

def callback(uuid: bytes) -> None:
    if uuid not in database:
        choice = input("Unknown card. Do you want to create a new user? (y/n)")
        if choice.lower() not in ["y", "yes", "ye"]:
            return
        
        new_user = user_manager.create_user()
        #The UUID's hex value is converted into bytes, which is written onto the NFC tag.
        nfc_reader.write_data(bytes.fromhex(new_user.uuid))
        database[new_user.uuid] = new_user
        # print("Select a user")
        # for i, user in enumerate(list(users.keys())):
        #     print(f"{i}: {user}")
        # index = int(input("Type in the number of the user you want to select."))
        
        print("Finished.")
        return
    
    #If the user is not present in the database, the default value will be "False".
    database[uuid.hex()] = not database.get(uuid.hex(), False) # Reverse the current status of the client who tagged their NFC tag, meaning that
                                                                #if they were present, they left, and vice versa.
    user_manager.update_user_presence(database[uuid.hex()])
    # response = requests.put(api, json = database)
    # print(f"Server Response: {response.json()}")

if __name__ == "__main__":
    user_manager.get_user("asd")
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    #Registers an event handler to an exit signal (Ctrl + c)
    atexit.register(nfc_reader.stop)