#!/usr/bin/env bash
# This file should only be ran inside the Insight Docker container. This script copies the config file into the volume at run time and starts the bot with any param$
chown -R insight:insight /app
cd /app
INSIGHT_START_CMD="$@"
for a in "$@"
do
 if [ "$a" = "-d" ] || [ "$a" = "--docker-init" ]; then
  cp /InsightDocker/Insight/default-config.ini /app
  cp /InsightDocker/Insight/README.md /app
  cp /InsightDocker/Insight/LICENSE.md /app
  cp /InsightDocker/Insight/scripts/Docker/master/README.md /app/Installation.md
  cp /InsightDocker/Insight/ChangeLog.md /app
  cp /InsightDocker/Insight/CCP.md /app
  echo "Successfully initialized the Docker volume with config and README files. Please edit the 'default-config.ini' with your configuration details and then rename it to 'config.ini'."
  exit 0
 fi
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