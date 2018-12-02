#!/usr/bin/env bash

pip3 install pyinstaller
cp /app/config.ini /InsightDocker/Insight
cp /app/Database.db /InsightDocker/Insight
mv /InsightDocker/sqlite-latest.sqlite /InsightDocker/Insight
cd /InsightDocker/Insight
pyinstaller scripts/PyInstaller.spec --clean
cp /InsightDocker/Insight/dist /app -R
cp /InsightDocker/Insight/distTest /app -R
cd /app
rm /InsightDocker -R
ldd --version
echo "Successfully created the Linux binary archive for Insight. You will find the archive in the dist folder. Your Database and config file have been copied into the distTest folder for testing to ensure the binary is working. Note: This application will not work on Linux distros with a glibc version below the listed version above."

