#!/usr/bin/env bash
# This file should only be ran inside the Insight Docker container. This script copies the config file into the volume at run time and starts the bot with any parameters passed.
git -C /InsightDocker/Insight pull
cp /InsightDocker/Insight/defult-config.ini /app
/InsightDocker/venv/bin/python3 /InsightDocker/Insight/Insight "$@"