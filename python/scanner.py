from typing import Callable, Union
from pn532 import PN532_I2C, MIFARE_CMD_AUTH_B
import time
#https://www.pythontutorial.net/python-concurrency/python-threading/
#https://www.pythontutorial.net/python-concurrency/python-threading-event/
from threading import Thread, Event

# https://github.com/gassajor000/pn532pi/tree/master/examples

# Create the Nfc class for reusability.
class Nfc:
    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    DEFAULT_BLOCK_NUMBER = 4
    #The __init__ method constructs an instance of the "Nfc" class.
    def __init__(self, read_callback: Callable[[int], None]) -> None:
        # FeliCa_card_detection.py
        self.read_callback = read_callback
        self.previousId = None
        self.previousTime = None
        self.thread = None
        self.stop_event = Event()
        self.nfc = PN532_I2C(debug = False, reset = 20, req = 16)
        
        self.nfc.SAM_configuration()

    #Private method so that it shouldn't be accessed by users.
    def __loop(self) -> None:
        print("NFC Reader ready.")
        #If "stop_event" is NOT set (i.e. the program is NOT stopped), enter the while loop.
        while not self.stop_event.is_set():
            try:
                self.stop_event.wait(.5)
                uid = self.nfc.read_passive_target(timeout=10)
                if uid is None:
                    continue
                
                # If we already encountered this ID within 15 seconds, sleep, refresh the current time and re-run the loop.
                # This is done in case the NFC tag is held in range for a longer period.
                if (uid == self.previousId and (self.previousTime is None or (time.time() - self.previousTime) < 15)):
                    #Refresh the time when the card was encountered last.
                    self.previousTime = time.time()
                    self.stop_event.wait(1)
                    continue

                print("Found a card!")
                # print(f"Card UID: {[hex(i) for i in uid]}")

                self.previousTime = time.time() #time.time gets the current time
                self.previousId = uid
                self.read_callback(self.read_data())
                
                # Wait 1 second before continuing
                self.stop_event.wait(1)

            except Exception as ex:
                print(f"Exception in loop: {ex.with_traceback(None)}")

    def start(self) -> None:
        self.stop_event.clear()
        #Create a new thread for the __loop method.
        #This allows the program to keep running while the __loop method keeps running.
        self.thread = Thread(target=self.__loop)
        #Name the thread so that it can be followed.
        self.thread.name = "NFC Polling Thread"
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        #Main thread tries to join the side thread. When successful, we are certain that the side thread stopped, therefore we are no longer polling.
        self.thread.join()
        self.nfc.cleanup()
        print("Program Finished.")

    def read_data(self) -> Union[bytes, None]:
        if not self.authenticate_card(Nfc.DEFAULT_BLOCK_NUMBER):
            return None
        data = self.nfc.mifare_classic_read_block(block_number=Nfc.DEFAULT_BLOCK_NUMBER)
        # print(f"Data from card: \n{[hex(i) for i in data]}")
        return data

    def write_data(self, data: bytes) -> None:
        if not self.authenticate_card(Nfc.DEFAULT_BLOCK_NUMBER):
            return
        choice = str(input("Are you sure you want to continue? THIS WILL ERASE DATA FROM THE CARD. (y/[n])") or "n")
        if choice.lower() not in ["y", "yes", "ye"]:
            return
        self.nfc.mifare_classic_write_block(Nfc.DEFAULT_BLOCK_NUMBER, data)
        
    #In order to scan MiFare NFC tags, we need to authenticate the card, as seen in the below example:
    #https://github.com/leon-anavi/rpi-examples/blob/master/PN532/python/rfid-save.py
    #https://www.youtube.com/watch?v=kpaQAqhv4R0
    def authenticate_card(self, block_id: int) -> bool:
        if not self.nfc.mifare_classic_authenticate_block(self.previousId, block_id, MIFARE_CMD_AUTH_B, Nfc.CARD_KEY):
            print(f"Failed to authenticate card block {block_id}.")
            return False
        return True