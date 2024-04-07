#!bin/sh
cd "$(dirname "$0")"

#Install virtualenv and then run the "start" file.
python -m pip install virtualenv
. start.sh