#!/usr/bin/env bash
# This file should only be ran inside the Insight Docker container. This script copies the config file into the volume at run time and starts the bot with any param$
chown -R insight:insight /app
cd /app
INSIGHT_START_CMD="$@"
cp -n /InsightDocker/Insight/default-config.ini /app
cp -n /InsightDocker/Insight/default-config.ini /app/config.ini
cp -n /InsightDocker/Insight/README.md /app
cp -n /InsightDocker/Insight/LICENSE.md /app
cp -n /InsightDocker/Insight/scripts/Docker/README.md /app/Installation.md
cp -n /InsightDocker/Insight/ChangeLog.md /app
cp -n /InsightDocker/Insight/CCP.md /app
chown -R insight:insight /app/*
chmod 644 /app/*.md
chmod 600 /app/config.ini
for a in "$@"
do
 if [ "$a" = "-b" ] || [ "$a" = "--build-binary" ]; then
  runuser -l insight -c "/InsightDocker/DockerBinBuild.sh"
 fi
 if [ "$a" = "-t" ] || [ "$a" = "--tests" ]; then
  runuser -l insight -c "/InsightDocker/DockerTests.sh"
 fi
  if [ "$a" = "--export-swagger-client" ]; then
  cd /InsightDocker/python-client
  zip -r /app/swagger-client-python.zip .
  exit 0
 fi
done
runuser -l insight -c "$INSIGHT_START_CMD"