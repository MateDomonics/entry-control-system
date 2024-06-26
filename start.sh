#!bin/bash
#https://saturncloud.io/blog/how-to-get-the-directory-where-a-bash-script-is-located/
#https://www.geeksforgeeks.org/dirname-command-in-linux-with-examples/
cd "$(dirname "$0")"

#https://stackoverflow.com/questions/13702425/source-command-not-found-in-sh-shell

#Fetch info on the branch and save the "head" of the local and remote branches.
git remote update
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

#If the two "heads" are not the same, do a "git pull".
if [ "$LOCAL" != "$REMOTE" ]
then
    git pull
    echo "Updates installed!"
    #https://stackoverflow.com/questions/12142031/run-commands-in-seperate-terminal-using-shell-script-bash
    x-terminal-emulator -e start.sh
    exit 0
fi

# Create the "data" folder if it doesn't exist.
if ! [ -d data ]
then
    echo "'data' folder doesn't exist, creating now."
    mkdir data
    cd data
    touch aws_access
    touch environment
    echo "Please fill in the 'aws_access' and 'environment' files as per the README."
    exit 0
fi

#https://sentry.io/answers/determine-whether-a-directory-exists-in-bash/
#If venv doesn't exist, create venv and install dependencies.
if ! [ -d venv ]
then
    echo "venv doesn't exist, creating venv."
    python3 -m venv venv
fi

#If we are still not in a venv, that probably means that the venv module is not present on the system, so install it.
if ! [ -d venv ]
then
    echo "Installing python virtualenv"
    python -m pip install virtualenv
    x-terminal-emulator -e start.sh
    exit 0
fi

source venv/bin/activate

#Update dependencies and choose which version of the app you want to run.
pip install -r dependencies.txt --upgrade
cd python
if [ "$1" == "main" ]
then
    python main.py
elif [ "$1" == "plot" ]
then
    python statistic_gatherer.py
else
    echo "Usage: bash start.sh [main/plot]"
fi

deactivate
