#!/usr/bin/env bash
# This file should only be ran inside the Insight Docker container. This script copies the config file into the volume at run time and starts the bot with any param$
/InsightDocker/PermissionSet.sh || exit 1
cd /app
for a in "$@"
do
 if [ "$a" = "-b" ] || [ "$a" = "--build-binary" ]; then
  exec /InsightDocker/DockerBinBuild.sh
 fi
 if [ "$a" = "-t" ] || [ "$a" = "--tests" ]; then
  exec /InsightDocker/DockerTests.sh
 fi
  if [ "$a" = "--export-swagger-client" ]; then
  cd /InsightDocker/python-client
  zip -r /app/swagger-client-python.zip .
  exit 0
 fi
done
exec "$@"