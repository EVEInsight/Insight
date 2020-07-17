#!/usr/bin/env bash
sudo chown -R insight:insight /app || exit 1
cp -n /InsightDocker/Insight/default-config.ini /app || exit 1
cp -n /InsightDocker/Insight/default-config.ini /app/config.ini || exit 1
cp -n /InsightDocker/Insight/README.md /app || exit 1
cp -n /InsightDocker/Insight/LICENSE.md /app || exit 1
cp -n /InsightDocker/Insight/scripts/Docker/README.md /app/Installation.md || exit 1
cp -n /InsightDocker/Insight/ChangeLog.md /app || exit 1
cp -n /InsightDocker/Insight/CCP.md /app || exit 1
sudo chown -R insight:insight /app || exit 1
sudo chmod 0600 /app/config.ini || exit 1