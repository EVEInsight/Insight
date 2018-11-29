#!/usr/bin/env bash
# This file should only be ran inside the Insight Docker container. This script copies the config file into the volume at run time and starts the bot with any parameters passed.
cp /InsightDocker/Insight/default-config.ini /app
cp /InsightDocker/Insight/README.md /app
cp /InsightDocker/Insight/LICENSE.md /app
cp /InsightDocker/Insight/Installation.md /app
cp /InsightDocker/Insight/ChangeLog.md /app
cp /InsightDocker/Insight/CCP.md /app
exec "$@"