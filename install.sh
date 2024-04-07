#!bin/sh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

#Install virtualenv and then run the "start" file.
python -m pip install virtualenv
source start.sh