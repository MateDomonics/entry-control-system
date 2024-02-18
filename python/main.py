from scanner import Nfc
import requests
import time

api = "https://eooorfidlkf4wow.m.pipedream.net"
#Key value pair where the key is the user's ID and the value shows whether they are present at the "venue" or not.
database = {}

def callback(uuid: int) -> None:
    #If the user is not present in the database, the default value will be "False".
    database[uuid] = not database.get(uuid, False) # Reverse the current status of the client who tagged their NFC tag, meaning that
                                                    #if they were present, they left, and vice versa.
    response = requests.put(api, json = database)
    print(f"Server Response: {response.json()}")

if __name__ == "__main__":
    # callback("test")
    # time.sleep(2)
    # callback("test")
    # exit(0)
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    input("Press RETURN to stop.\n")
    nfc_reader.stop()