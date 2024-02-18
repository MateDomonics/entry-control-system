from scanner import Nfc
import requests
from hashlib import md5

#Use the md5 hash of a user's full name and email address.
#This ensures a unique user ID.
fake_user1 = "John;Doe;jodoe@test.com"
fake_user2 = "Jane;Doe;jadoe@test.com"

api = "https://eooorfidlkf4wow.m.pipedream.net"
#Key value pair where the key is the user's ID and the value shows whether they are present at the "venue" or not.
database = {}
users = [fake_user1, fake_user2]
nfc_reader:Nfc = None

def callback(uuid: int) -> None:
    if uuid not in users:
        choice = input("Unknown card. Do you want to assign the card to a user? (y/n)")
        if choice.lower() not in ["y", "yes", "ye"]:
            return
        
        print("Select a user")
        for i, user in enumerate(users):
            print(f"{i}: {user}")
        index = int(input("Type in the number of the user you want to select."))
        nfc_reader.write_data(md5(users[index].encode()).digest(), uuid)

        print("Finished.")
        return
    
    #If the user is not present in the database, the default value will be "False".
    database[uuid] = not database.get(uuid, False) # Reverse the current status of the client who tagged their NFC tag, meaning that
                                                    #if they were present, they left, and vice versa.
    response = requests.put(api, json = database)
    print(f"Server Response: {response.json()}")

if __name__ == "__main__":
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    input("Press RETURN to stop.\n")
    nfc_reader.stop()