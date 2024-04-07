#!bin/sh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

#Fetch info on the branch and save the "head" of the local and remote branches.
git remote update
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

#If the two "heads" are not the same, do a "git pull".
if [ "$LOCAL" != "$REMOTE" ]
then
    git pull
    echo "Updates installed!"
    exit 1
fi

exit 0