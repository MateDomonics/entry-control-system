from typing import Callable
from pn532pi import Pn532I2c, Pn532
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
        self.i2c = Pn532I2c(1)
        self.nfc = Pn532(self.i2c)
        self.nfc.begin()
        
        versiondata = self.nfc.getFirmwareVersion()
        if versiondata == 0:
            print("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")
        print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                    (versiondata >> 8) & 0xFF))
        
        self.nfc.setPassiveActivationRetries(0xFF)
        self.nfc.SAMConfig()

    #Private method so that it shouldn't be accessed by users.
    def __loop(self) -> None:
        while self.run:
            systemCode = 0xFFFF
            requestCode = 0x01  # System Code request

            # Wait for an FeliCa type cards.
            # When one is found, some basic information such as IDm, PMm, and System Code are retrieved.
            ret, idm, pwm, systemCodeResponse = self.nfc.felica_Polling(systemCode, requestCode, 5000)

            #If the ret's value is anything other than 1, sleep and retry, because we haven't found an NFC tag.
            if (ret != 1):
                time.sleep(.5)
                continue
            
            # If we already encountered this ID within 1 seconds, sleep, refresh the current time and re-run the loop.
            # This is done in case the NFC tag is held in range for a longer period.
            if (idm == self.previousId and (time.time() - self.previousTime) < 1):
                #Refresh the time when the card was encountered last.
                self.previousTime = time.time()
                time.sleep(.5)
                continue

            print("Found a card!")
            #Convert the integert from each to hexadecimal number
            #Makes it easier to read
            print("  IDm : {}".format(hex(int.from_bytes(idm))))
            print("  PWm: {}".format(hex(int.from_bytes(pwm))))
            print("  System Code: {:x}".format(hex(int.from_bytes(systemCode))))
            self.previousTime = time.time() #time.time gets the current time
            self.previousId = idm
            self.read_data()

            # Wait 1 second before continuing
            time.sleep(1)

    def start(self) -> None:
        self.run = True
        #Create a new thread for the __loop method.
        #This allows the program to keep running while the __loop method keeps running.
        self.thread = Thread(target=self.__loop)
        #Name the thread so that it can be followed.
        self.thread.name = "NFC Polling"
        self.thread.start()

    def stop(self) -> None:
        self.run = False
        #Main thread tries to join the side thread. When successful, we are certain that the side thread stopped, therefore we are no longer polling.
        self.thread.join()
        print("Program Finished.")

    def read_data(self):
        # FeliCa_card_read.py
        serviceCodeList = [0x000B]
        blockList = [0x8000, 0x8001, 0x8002]
        #Requests the NFC reader to read in values.
        ret, blocks = self.nfc.felica_ReadWithoutEncryption(serviceCodeList, blockList)
        #If the value is anything other than -1, the read was unsuccessful.
        if (ret != 1):
            print("error")
            return
        
        uuid = hex(int.from_bytes(blocks))
        #If successful, print the data stored on the NFC Tag.
        print(f"  BlockData: {uuid}")
        self.read_callback(uuid)