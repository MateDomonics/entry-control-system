# KapU - Entry Control System

## Summary

This is the GitHub Repository for KapU, a Fourth Year Project developed by Máté Domonics, studying at SETU Waterford.
The project utilizes a Raspberry Pi, along with a PN532 NFC Scanner module to scan NFC tags and interact with a DynamoDB Database to check if a customer's UID is present.

[Official GitHub Pages Website](https://matedomonics.github.io/entry-control-system/)

## User Setup

1. Clone the repository onto a Raspberry Pi which has been set up with the capability to run a PN532 NFC HAT Module.
2. Run the `start` bash script, which will initialise a python virtual environment and run the program automatically.

## Developer Setup

This project is being developed on Windows, using WSL (Windows Subsystem for Linux) and VSC (Visual Studio Code).

1. Download WSL, clone the repo and open up the repo's directory in WSL.
2. Run the `code` command in the directory to start VSC using WSL in the directory.

## Developer Log

### January 2nd, 2024

- Set up project.
- Created the initial, concept version of the project based on the [pn532pi library](https://pypi.org/project/pn532pi/).
- Fried the first NFC HAT module, so there also was a workaround implemented temporarily to show that the code theoretically worked.

### January 21st, 2024

- Abandoned the pn532pi libray due to many difficulties with it. Instead, I found another GitHub repo that seemed similar to the library, and I took the `i2c.py` and `pn532.py` files from it as a base.
- Implemented python virtual environments to help with running the program.

### January 26th, 2024

- Cleaned up the code to fully remove code that depended on the python library.
- Fixed dependencies for the project.
- Implemented the scanning successfully with most NFC-based devices.
- Experimented with writing to NFC tag, unsuccessful.

TO-DO:

- Can't scan NFC tag that came with Raspberry Pi.

### February 9th, 2024

- GitHub Pages website implemented.

### February 18th, 2024

- Fixed issue with not being able to scan NFC tags that came with Raspberry Pi.
- Created bash script that automatically creates a virtual environment if not present and switches to it.
- Fixing imports, adding comments.
- Implemented the ability to write to NFC Tags.
- Wrote documentation in `README.md`, which will be kept up-to-date from now on.
- Merged `proof-of-concept` branch to `main`

TO-DO:

- Move on from using fake users to test writing and reading to actually using DynamoDB on AWS.

### February 25th, 2024

- Made sure to NOT upload my AWS credentials to GitHub like an idiot.
- Added the ability to create a new user on DynamoDB using the program.
- Added the ability to get a user from DynamoDB.
- Tried to implement the ability to update a user on DynamoDB. (Doesn't work yet.)
- Fixed a GPIO warning that was thrown everytime because no cleanup was done.
- Reduced print statements to prepare for a "release build".

TO-DO:

- Boto3 documentation is absolutely shocking, so the update method still doesn't work. Try figure it out.

## Sources

- [PN532-NFC-HAT GitHub Repository](https://github.com/soonuse/pn532-nfc-hat)

Using parts of this github repo (pn532.py, i2c.py).

- [FakeRPi GitHub Repository](https://github.com/sn4k3/FakeRPi)

Used to help with developing Raspberry Pi programs on Windows.
