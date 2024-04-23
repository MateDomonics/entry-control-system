# Makes a package of the "pn532" folder.
# Easier to use methods from the python files.
# Also saves us from having to specify the file path when trying to import.
from .i2c import PN532_I2C
from .pn532 import MIFARE_CMD_AUTH_B, PN532Error