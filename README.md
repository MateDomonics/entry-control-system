# KapU - Entry Control System

## Summary

This is the GitHub Repository for KapU, a Fourth Year Project developed by Máté Domonics, studying at SETU Waterford.
The project utilizes a Raspberry Pi, along with a PN532 NFC Scanner module to scan NFC tags and interact with a DynamoDB Database to check if a customer's UID is present.

## User Setup

1. Clone the repository onto a Raspberry Pi which has been set up with the capability to run a PN532 NFC HAT Module.
2. Run the `start` bash script, which will initialise a python virtual environment and run the program automatically.

## Developer Setup

This project is being developed on Windows, using WSL (Windows Subsystem for Linux) and VSC (Visual Studio Code).

1. Download WSL, clone the repo and open up the repo's directory in WSL.
2. Run the `code` command in the directory to start VSC using WSL in the directory.

## Developer Log



## Sources

- https://github.com/soonuse/pn532-nfc-hat
Not supported on Windows, had to use Windows Subsystem for Linux to develop.

- https://pypi.org/project/pn532pi/

- https://github.com/sn4k3/FakeRPi