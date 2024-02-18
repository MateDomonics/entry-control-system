from typing import Callable
from pn532 import PN532_I2C, MIFARE_CMD_AUTH_B
import time
from threading import Thread

# https://github.com/gassajor000/pn532pi/tree/master/examples

# Create the Nfc class for reusability.
class Nfc():
    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    #The __init__ method returns with an instance of the "Nfc" class.
    def __init__(self, read_callback: Callable[[int], None]) -> "Nfc":
        # FeliCa_card_detection.py
        self.read_callback = read_callback
        self.previousId = None
        self.previousTime = None
        self.thread = None
        self.run = True
        self.nfc = PN532_I2C(debug = False, reset = 20, req = 16)

        versiondata = self.nfc.get_firmware_version()
        # Output, without formatting: (50, 1, 6, 7)
        #                        Checksum, major, minor, tertiary

        print(f"Current version of the PN532 board: {versiondata[1]}.{versiondata[2]}.{versiondata[3]}")
        
        self.nfc.SAM_configuration()

    #Private method so that it shouldn't be accessed by users.
    def __loop(self) -> None:
        while self.run:
            try:
                uid = self.nfc.read_passive_target(timeout=10)
                if uid is None:
                    continue
                
                # If we already encountered this ID within 15 seconds, sleep, refresh the current time and re-run the loop.
                # This is done in case the NFC tag is held in range for a longer period.
                if (uid == self.previousId and (self.previousTime is None or (time.time() - self.previousTime) < 15)):
                    #Refresh the time when the card was encountered last.
                    self.previousTime = time.time()
                    time.sleep(1)
                    continue

                print("Found a card!")
                print(f"Card UID: {[hex(i) for i in uid]}")

                self.previousTime = time.time() #time.time gets the current time
                self.previousId = uid
                # self.read_callback(int.from_bytes(self.read_data(uid)))
                self.read_data(uid)
                
                # Wait 1 second before continuing
                time.sleep(1)

            except Exception as ex:
                print(f"Exception in loop: {ex}")

    def start(self) -> None:
        self.run = True
        #Create a new thread for the __loop method.
        #This allows the program to keep running while the __loop method keeps running.
        self.thread = Thread(target=self.__loop)
        #Name the thread so that it can be followed.
        self.thread.name = "NFC Polling Thread"
        self.thread.start()

    def stop(self) -> None:
        self.run = False
        #Main thread tries to join the side thread. When successful, we are certain that the side thread stopped, therefore we are no longer polling.
        self.thread.join()
        print("Program Finished.")

    def read_data(self, uid: bytearray) -> bytes:
        for x in range(0,21):
            if not self.authenticate_card(uid, block_id=x):
                continue
            data = self.nfc.mifare_classic_read_block(block_number=x)
            print(f"Data from card block {x}: \n{[hex(i) for i in data]}")
            # return data

    def write_data(self, uid: bytes, data: int):
        if not self.authenticate_card(uid):
            return None
        choice = str(input("Are you sure you want to continue? THIS WILL ERASE DATA FROM THE CARD. (y/[n])") or "n")
        if choice.lower() not in ["y", "yes", "ye"]:
            return
        self.nfc.mifare_classic_write_block(4, data.to_bytes(16))
        
    def authenticate_card(self, uid: bytearray, block_id: int = 4) -> bool:
        if not self.nfc.mifare_classic_authenticate_block(uid, block_id, MIFARE_CMD_AUTH_B, Nfc.CARD_KEY):
            print(f"Failed to authenticate card block {block_id}.")
            return False
        return True