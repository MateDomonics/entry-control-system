from typing import Dict
from scanner import Nfc
import atexit
from os import path
from user_creation import User_manager, User

#Key value pair where the key is the user's ID and the value shows whether they are present at the "venue" or not.
database: Dict[str, User] = {}
nfc_reader:Nfc = None
#Use the current python file's location to find the "aws_access" file which is one level above the python file.
user_manager = User_manager.load_access(path.join(path.dirname(path.dirname(__file__)), "aws_access"))

def callback(_uuid: bytes) -> None:
    uuid = _uuid.hex()
    if uuid not in database and not get_user_from_database(uuid):
        choice = input("Unknown card. Do you want to create a new user? (y/n)")
        if choice.lower() not in ["y", "yes", "ye"]:
            return
        
        new_user = user_manager.create_user()
        if new_user is None:
            return
        
        if not nfc_reader.is_same_card_present():
            print("Please keep the card on the reader.")
            while not nfc_reader.is_same_card_present():
                pass

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
    database[uuid].inside_facility = not database[uuid].inside_facility # Reverse the current status of the client who tagged their NFC tag, meaning that
                                                                        #if they were present, they left, and vice versa.
    if user_manager.update_user_presence(database[uuid]):
        print(f"Welcome {database[uuid].first_name}!" if database[uuid].inside_facility else "Have a nice day, see you soon!")
    else:
        print("Presence update failed.")
    # response = requests.put(api, json = database)
    # print(f"Server Response: {response.json()}")

def get_user_from_database(uuid: str) -> bool:
    user = user_manager.get_user(uuid)
    print(user)
    if user is None:
        return False
    database[user.uuid] = user
    return True

if __name__ == "__main__":
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    #Registers an event handler to an exit signal (Ctrl + c)
    atexit.register(nfc_reader.stop)