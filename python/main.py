from typing import Dict, Union
from scanner import Nfc
import atexit
from os import path
from user_creation import User_manager, User
from sys import stderr
from datetime import datetime
from api import Api
from statistic_gatherer import Gatherer

#Key value pair where the key is the user's ID and the value shows whether they are present at the "venue" or not.
#This is the "local database". For production, I would install a NoSQL database locally as a Docker Image and interact with that.
database: Dict[str, User] = {}
is_stopped = False
nfc_reader:Nfc = None

#Use the current python file's location to find the supplementary files in the "data" folder.
#These files define the API Key, the Table Name we are working on and the statistics generated about the facility.
datastore = path.join(path.dirname(path.dirname(__file__)), "data")

api = Api.from_file(path.join(datastore, "aws_access"))
user_manager = User_manager.from_file(api, path.join(datastore, "environment"))
gatherer = Gatherer.from_file(api, path.join(datastore, "statistics"), user_manager.table_name)

"""
This is the method that runs when we detect an NFC tag.
Check if the user we found on the NFC tag is present locally or in the cloud. If user is not present, call the "create_new_user" function.
Confirm that the user being scanned has an active subscription. If not, tell them when the subscription expired.
Lastly, if they have a valid subscription, call the "update_user_presence" function.
"""
def callback(_uuid: Union[bytes, None]) -> None:
    if _uuid is None:
        return
    
    uuid = _uuid.hex()
    if uuid not in database and not get_user_from_database(uuid):
        create_new_user()
        return
    
    if not database[uuid].validate_subscription():
        print(f"Your subscription has expired at {datetime.fromtimestamp(database[uuid].active_subscription)} , please contact a member of staff for assistance.")
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

"""
Offer to create a new user.
If the user moves the NFC tag from the reader while we try to write, warn them and try again.
Then write the information we got onto the NFC tag presented and add them to the local- and cloud database.
"""
def create_new_user() -> None:
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
    
    # Error handling if we couldn't write to the NFC tag.
    if not write_success:
        print("Couldn't write to card or writing to card was interrupted, please try again.", file=stderr)
        return
    
    save_success = user_manager.save_user(new_user)
    
    # Error handling if we couldn't upload to AWS.
    if not save_success:
        print("Couldn't upload to AWS, please try again.", file=stderr)
        return
    
    database[new_user.uuid] = new_user
    print("Finished.")
    return

"""
Send an update to the local- and cloud database that the user has left or entered the facility.
Depending on the state of the user, welcome them or bid them farewell.
"""
def update_user_presence(uuid: str) -> None:
    #If the user is not present in the database, the default value will be "False".
    database[uuid].inside_facility = not database[uuid].inside_facility # Reverse the current status of the client who tagged their NFC tag, meaning that
                                                                        #if they were present, they left, and vice versa.
    if user_manager.update_user_presence(database[uuid]):
        print(f"Welcome {database[uuid].first_name}!" if database[uuid].inside_facility else f"Have a nice day {database[uuid].first_name}, see you soon!")
    else:
        print(f"Presence update failed for {database[uuid].first_name}.", file=stderr)

"""
Stop all the threads, join them back into the main thread and tell the user that the program finished.
"""
def stop() -> None:
    # Prevent multiple stop() calls.
    global is_stopped
    if is_stopped:
        return
    
    print("\nStopping program...")
    nfc_reader.stop()
    gatherer.stop()
    nfc_reader.thread.join()
    gatherer.thread.join()
    
    is_stopped = True
    print("Program Finished.")

if __name__ == "__main__":
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    gatherer.start()
    #Registers an event handler to an exit signal (Ctrl + c)
    atexit.register(stop)
    try:
        while True:
            # Wait for the user to press ENTER in order to generate the plot based on the statistics.
            input("Press RETURN to see statistics\n")
            gatherer.generate_plot()
    except KeyboardInterrupt:
        stop()
