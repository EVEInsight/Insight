#!/usr/bin/env bash
# This is an example start script to run Insight in the background using screen.
# This script navigates to the Insight git directory, updates from git, and starts Insight using a python
# virtual environment named venv in a screen session called eveInsight
Script=$(readlink -f "$0")
SPath=$(dirname "$Script")
cd $SPath
cd ..
git pull
screen -dmS eveInsight venv/bin/python3 Insight -api