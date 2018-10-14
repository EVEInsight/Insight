#!/usr/bin/env bash
# This is a testing script to automatically compile and run a fresh Insight copy.
# You probably should not use this script.

Script=$(readlink -f "$0")
SPath=$(dirname "$Script")
cd $SPath/..
scripts/insight_stop.sh
rm venv -R
git pull || exit 1
scripts/AutoSetup.sh || exit 1
source venv/bin/activate
pip3 install --upgrade pyinstaller || exit 1
pyinstaller scripts/PyInstaller.spec --clean || exit 1
screen -dmS eveInsight distTest/Insight || exit 1
echo 'Insight bin version started.'
