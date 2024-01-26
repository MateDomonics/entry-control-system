from typing import Callable
from pn532 import PN532_I2C
import time
from threading import Thread

# https://github.com/gassajor000/pn532pi/tree/master/examples

# Create the Nfc class for reusability.
class Nfc():
    #The __init__ method returns with an instance of the "Nfc" class.
    def __init__(self, read_callback: Callable[[str], None]) -> "Nfc":
        # FeliCa_card_detection.py
        self.read_callback = read_callback
        self.previousId = None
        self.previousTime = None
        self.thread = None
        self.run = True
        # self.i2c = Pn532I2c(1)
        # self.nfc = Pn532(self.i2c)
        self.nfc = PN532_I2C(debug = True, reset = 20, req = 16)
        #self.nfc.begin()

        versiondata = self.nfc.get_firmware_version()
        # Output, without formatting: (50, 1, 6, 7)
        #                        Checksum, major, minor, tertiary

        # print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
        #                                                             (versiondata >> 8) & 0xFF))
        print(f"Current version of the PN532 board: {versiondata[1]}.{versiondata[2]}.{versiondata[3]}")
        
        # self.nfc.setPassiveActivationRetries(0xFF)
        # self.nfc.SAMConfig()

    #Private method so that it shouldn't be accessed by users.
    def __loop(self) -> None:
        while self.run:
            try:
                uid = self.nfc.read_passive_target()
                if uid is None:
                    # uid = self.nfc.read_passive_target(card_baud=)
                    continue
                print(f"Card UID: {uid}")
                
                # If we already encountered this ID within 1 seconds, sleep, refresh the current time and re-run the loop.
                # This is done in case the NFC tag is held in range for a longer period.
                if (uid == self.previousId and (self.previousTime is None or (time.time() - self.previousTime) < 1)):
                    #Refresh the time when the card was encountered last.
                    self.previousTime = time.time()
                    time.sleep(.5)
                    continue

                self.previousTime = time.time() #time.time gets the current time
                self.previousId = uid
                self.read_data()

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

    def read_data(self):
        data = self.nfc.mifare_classic_read_block()
        if data == None:
            print("Read error!")
            time.sleep(1)
            return
        
        print("Found a card!")
        print(f"Data from card: \n{data.hex()}")