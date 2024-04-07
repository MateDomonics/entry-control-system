#bin/bash
#In order to not have to carry around a mouse and keyboard, I made a new system service that automatically starts with the Raspberry Pi.
#This means that all I need to do is connect my Pi to a monitor to show output.
cd "$(dirname "$0")"

sleep 30

x-terminal-emulator -e --wait start.sh