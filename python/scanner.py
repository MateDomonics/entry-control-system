from typing import Callable, Union
from pn532 import PN532_I2C, MIFARE_CMD_AUTH_B, PN532Error
import time
#https://www.pythontutorial.net/python-concurrency/python-threading/
#https://www.pythontutorial.net/python-concurrency/python-threading-event/
from threading import Thread, Event
import traceback
from sys import stderr

# https://github.com/gassajor000/pn532pi/tree/master/examples

class Nfc:
    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    DEFAULT_BLOCK_NUMBER = 4

    """
    Construct an instance of the "Nfc" class.
    Also call the SAM_configuration() function which sets the configuration for the NFC reader.
    """
    def __init__(self, read_callback: Callable[[Union[bytes, None]], None]) -> None:
        # FeliCa_card_detection.py
        self.read_callback = read_callback
        self.previousId = None
        self.previousTime = None
        self.thread = None
        self.stop_event = Event()
        self.nfc = PN532_I2C(debug = False, reset = 20, req = 16)
        
        self.nfc.SAM_configuration()

    """
    Blocking method, requiring its own thread, therefore its private.
    This class initiates NFC reading and saves the data if we find a valid tag.
    """
    def __loop(self) -> None:
        print("NFC Reader ready.")
        #If "stop_event" is NOT set (i.e. the program is NOT stopped), enter the while loop.
        while not self.stop_event.is_set():
            try:
                #Give a little bit of CPU time for other processes. Helps with general performance from what I found.
                self.stop_event.wait(.5)
                #NFC Reader reads for 10 seconds. If nothing is found, go back to the top of the loop and try again.
                uid = self.nfc.read_passive_target(timeout=10)
                if uid is None:
                    continue
                
                # If we already encountered this ID within 5 seconds, sleep, refresh the current time and re-run the loop.
                # This is done in case the NFC tag is held in range for a longer period, to prevent re-reading the same tag.
                if (uid == self.previousId and (self.previousTime is None or (time.time() - self.previousTime) < 5)):
                    self.previousTime = time.time()
                    self.stop_event.wait(1)
                    continue

                #If the above passed, we can assume we have a new card, so update the current time and UID, then read in the data from the tag.
                self.previousTime = time.time()
                self.previousId = uid
                self.read_callback(self.read_data())
                
                # Wait 1 second before continuing
                self.stop_event.wait(1)

            except Exception:
                print(f"Exception in loop: {traceback.format_exc()}")

    """
    Helper method to make sure that the card we found earlier is still present.
    """
    def is_same_card_present(self) -> bool:
        return self.previousId == self.nfc.read_passive_target(timeout=1)

    """
    Start the loop by clearing the "stop_event" Event. The loop listens for NFC tags on its own, individual CPU thread.
    If we didn't assign a thread, other parts of the program wouldn't function until the main loop finishes.
    """
    def start(self) -> None:
        self.stop_event.clear()
        #Create a new thread for the __loop method.
        #This allows the program to keep running while the __loop method keeps running.
        self.thread = Thread(target=self.__loop)
        #Name the thread so that it can be followed.
        self.thread.name = "NFC Polling Thread"
        self.thread.start()

    """
    Stop the loop by setting the "stop_event" Event.
    I also wait for the CPU thread to die and then cleanup the General Purpose Input/Output pins.
    This is done to prevent warnings from popping up and to signal to the OS that those pins are no longer in use.
    """
    def stop(self) -> None:
        self.stop_event.set()
        self.nfc.cleanup()

    """
    Read in the data present on the NFC tag.
    First, we authenticate the card to allow us access and then we read the 4th memory block, which contains the UUID.
    """
    def read_data(self) -> Union[bytes, None]:
        if not self.authenticate_card(Nfc.DEFAULT_BLOCK_NUMBER):
            return None
        data = self.nfc.mifare_classic_read_block(block_number=Nfc.DEFAULT_BLOCK_NUMBER)
        return data

    """
    Write data onto the NFC tag.
    Again, authenticate the card to allow access, then make sure the user knows the risk of overwriting data on an NFC tag.
    Once confirmed, write the data to memory block 4.
    """
    def write_data(self, data: bytes) -> bool:
        if not self.authenticate_card(Nfc.DEFAULT_BLOCK_NUMBER):
            return False
        choice = str(input("Are you sure you want to continue? \033[91mTHIS WILL ERASE DATA FROM THE CARD.\033[0m (y/[n])") or "n")
        if choice.lower() not in ["y", "yes", "ye"]:
            return False
        self.nfc.mifare_classic_write_block(Nfc.DEFAULT_BLOCK_NUMBER, data)
        return True
        
    """
    Authenticate the MIFARE cards, due to issues with accessing the memory on them for reading and writing.
    https://github.com/leon-anavi/rpi-examples/blob/master/PN532/python/rfid-save.py
    https://www.youtube.com/watch?v=kpaQAqhv4R0
    """
    def authenticate_card(self, block_id: int) -> bool:
        try:
            if not self.nfc.mifare_classic_authenticate_block(self.previousId, block_id, MIFARE_CMD_AUTH_B, Nfc.CARD_KEY):
                print(f"Failed to authenticate card block {block_id}.", file=stderr)
                return False
            return True
        except PN532Error:
            print("Authentication failed. Card was moved during authentication.")
