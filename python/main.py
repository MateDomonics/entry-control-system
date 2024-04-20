from typing import Dict
from scanner import Nfc
import atexit
from os import path
from user_creation import User_manager, User
from sys import stderr

#Key value pair where the key is the user's ID and the value shows whether they are present at the "venue" or not.
#This is the "local database". For production, I would install a NoSQL database locally as a Docker Image and interact with that.
database: Dict[str, User] = {}
nfc_reader:Nfc = None

#Use the current python file's location to find the "aws_access" file which is one level above the python file.
user_manager = User_manager.load_access(path.join(path.dirname(path.dirname(__file__)), "aws_access"))

"""
This is the method that gets run when we detect an NFC tag.
Check if the user we found on the NFC tag is present locally or in the cloud, and if not, offer to create a new user.
If the user moves the NFC tag from the reader while we try to write, warn them and try again.
Then write the information we got onto the NFC tag presented and add them to the local- and cloud database.
Lastly, welcome them to the facility, or bid them farewell.
"""
def callback(_uuid: bytes) -> None:
    uuid = _uuid.hex()
    if uuid not in database and not get_user_from_database(uuid):
        configure_new_user()
        return
    
    update_user_presence(uuid)

"""
Get the user from the DynamoDB database and save them locally to prevent unnecessary API calls.
"""
def get_user_from_database(uuid: str) -> bool:
    user = user_manager.get_user(uuid)
    if user is None:
        return False
    database[user.uuid] = user
    return True

def configure_new_user() -> None:
    choice = input("Unknown card. Do you want to create a new user? (y/n)")
    
    if choice.lower() not in ["y", "yes", "ye"]:
        return
    
    new_user = user_manager.configure_user()
    
    if not nfc_reader.is_same_card_present():
        print("Please keep the card on the reader.")
        while not nfc_reader.is_same_card_present():
            pass

    #The UUID's hex value is converted into bytes, which is written onto the NFC tag.
    write_success = nfc_reader.write_data(bytes.fromhex(new_user.uuid))
    
    if not write_success:
        print("Couldn't write to card or writing to card was interrupted, please try again.", file=stderr)
        return
    
    save_success = user_manager.save_user(new_user)
        
    if not save_success:
        print("Couldn't upload to AWS, please try again.", file=stderr)
        return
    
    database[new_user.uuid] = new_user
    print("Finished.")
    return
    
def update_user_presence(uuid: str) -> None:
    #If the user is not present in the database, the default value will be "False".
    database[uuid].inside_facility = not database[uuid].inside_facility # Reverse the current status of the client who tagged their NFC tag, meaning that
                                                                        #if they were present, they left, and vice versa.
    if user_manager.update_user_presence(database[uuid]):
        print(f"Welcome {database[uuid].first_name}!" if database[uuid].inside_facility else f"Have a nice day {database[uuid].first_name}, see you soon!")
    else:
        print(f"Presence update failed for {database[uuid].first_name}.", file=stderr)

if __name__ == "__main__":
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    #Registers an event handler to an exit signal (Ctrl + c)
    atexit.register(nfc_reader.stop)