#!bin/sh
#https://saturncloud.io/blog/how-to-get-the-directory-where-a-bash-script-is-located/
#https://www.geeksforgeeks.org/dirname-command-in-linux-with-examples/
cd "$(dirname "$0")"

#https://stackoverflow.com/questions/13702425/source-command-not-found-in-sh-shell
. update.sh

#If the previous exit code was 1 (i.e. update.sh successfully ran and exited with code 1), run "start.sh" in a new terminal window.
if [ $? -eq 1 ]
then
    #https://stackoverflow.com/questions/12142031/run-commands-in-seperate-terminal-using-shell-script-bash
    x-terminal-emulator -e start.sh
    exit 0
fi

#https://sentry.io/answers/determine-whether-a-directory-exists-in-bash/
#If venv doesn't exist, create venv and install dependencies.
if ! [ -d venv ]
then
    echo "venv doesn't exist, creating venv."
    python3 -m venv venv
fi

#If we are still not in a venv, that probably means that the venv module is not present on the system, so install it by running "install.sh".
if ! [ -d venv ]
then
    echo "Installing python virtualenv"
    x-terminal-emulator -e install.sh
    exit 0
fi

#If not in venv, activate venv.
if [ "$VIRTUAL_ENV" == "" ]
then
    source venv/bin/activate
fi

#Update dependencies and run "main.py"
pip install -r dependencies.txt --upgrade
cd python
python main.py