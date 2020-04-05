#!/usr/bin/env bash
chown -R insight:insight /app
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