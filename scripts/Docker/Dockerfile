FROM swaggerapi/swagger-codegen-cli:2.4.13 as SwaggerBuilder

FROM openjdk:12-jdk-alpine as SwaggerRunner
COPY --from=SwaggerBuilder /opt/swagger-codegen-cli/swagger-codegen-cli.jar ./swagger-codegen-cli.jar
RUN java -jar ./swagger-codegen-cli.jar generate \
 -i "https://esi.evetech.net/_latest/swagger.json" \
 -l python \
 -o /python-client

#FROM maven:3-jdk-8-alpine as SwaggerRunner #newest Docker but there are issues so use old one for now
#RUN apk add --no-cache git
#RUN git clone https://github.com/swagger-api/swagger-codegen.git
#WORKDIR /swagger-codegen
#RUN mvn clean package
#RUN java -jar modules/swagger-codegen-cli/target/swagger-codegen-cli.jar generate \
# -i "https://esi.tech.ccp.is/_latest/swagger.json" \
# -l python \
# -o /python-client

FROM alpine:latest as SDE
RUN wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
RUN wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2.md5
RUN md5sum -c sqlite-latest.sqlite.bz2.md5
RUN bunzip2 sqlite-latest.sqlite.bz2

FROM python:3.6-buster
LABEL maintainer="nathan@nathan-s.com"
LABEL url="https://github.com/Nathan-LS/Insight"

ENV DB_DRIVER="sqlite3"
ENV SQLITE_DB_PATH="Database.db"
ENV HEADERS_FROM_EMAIL=""
ENV DISCORD_TOKEN=""
ENV CCP_CLIENT_ID=""
ENV CCP_SECRET_KEY=""
ENV CCP_CALLBACK_URL=""
ENV DISCORDBOTS_APIKEY=""
ENV INSIGHT_STATUS_CPUMEM=""
ENV INSIGHT_STATUS_VERSION_FEEDCOUNT=""
ENV INSIGHT_STATUS_TIME=""
ENV LIMITER_GLOBAL_TICKETS=""
ENV LIMITER_GLOBAL_INTERVAL=""
ENV LIMITER_DM_TICKETS=""
ENV LIMITER_DM_INTERVAL=""
ENV LIMITER_GUILD_TICKETS=""
ENV LIMITER_GUILD_INTERVAL=""
ENV LIMITER_CHANNEL_TICKETS=""
ENV LIMITER_CHANNEL_INTERVAL=""
ENV LIMITER_USER_TICKETS=""
ENV LIMITER_USER_INTERVAL=""
ENV REDIS_HOST=""
ENV REDIS_PORT=""
ENV REDIS_PASSWORD=""
ENV REDIS_DB=""
ENV REDIS_PURGE=""
ENV REDIS_CONNECTIONS_MIN=""
ENV REDIS_CONNECTIONS_MAX=""
ENV POSTGRES_HOST=""
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
ENV POSTGRES_DB=""
ENV REDIS_TIMEOUT=""
ENV REDIS_SSL=""
ENV POSTGRES_POOLSIZE=""
ENV POSTGRES_POOLOVERFLOW=""
ENV SUBSYSTEM_CACHE_THREADS=""
ENV SUBSYSTEM_CACHE_LASTSHIP_PRECACHE=""
ENV SUBSYSTEM_CACHE_LASTSHIP_TTL=""
ENV CRON_SYNCCONTACTS=""
ENV INSIGHT_ADMINS=""
ENV 8BALL_RESPONSES=""

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
 apt-utils \
 curl \
 ca-certificates \
 gnupg \
 lsb-release
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install -y \
 git \
 build-essential \
 zip \
 libpq-dev \
 sudo
RUN rm -rf /var/lib/apt/lists/*

RUN mkdir /InsightDocker /app /home/insight
RUN addgroup -gid 1007 insight
RUN useradd --system --shell /bin/bash --home /app -u 1006 -g insight insight
RUN chown insight:insight /InsightDocker /app /home/insight
USER insight
WORKDIR /InsightDocker
COPY --from=SwaggerRunner /python-client ./python-client
COPY --from=SDE /sqlite-latest.sqlite ./sqlite-latest.sqlite
WORKDIR /InsightDocker/Insight
COPY ./Insight ./Insight
COPY ./scripts ./scripts
COPY ./docs ./docs
COPY ./*.md ./
COPY ./*.txt ./
COPY ./default-config.ini ./
WORKDIR /InsightDocker
RUN cp /InsightDocker/python-client /InsightDocker/python-client-2 -R
USER root
RUN chown -R insight:insight /InsightDocker/Insight
RUN find /InsightDocker/Insight -type f -exec chmod 0644 {} \;
RUN find /InsightDocker/Insight -type d -exec chmod 0755 {} \;
RUN pip3 install wheel setuptools
WORKDIR /InsightDocker/python-client-2
RUN python3 setup.py install
WORKDIR /InsightDocker/Insight
RUN pip3 install --upgrade -r requirements.txt
RUN find /InsightDocker/Insight/scripts/Docker/ -maxdepth 1 -name "*.sh" -type f -exec cp {} /InsightDocker/ \;
RUN rm /InsightDocker/python-client-2 -R
RUN find /InsightDocker/ -maxdepth 1 -name "*.sh" -type f -exec chmod 0500 {} \;
RUN find /InsightDocker/ -maxdepth 1 -name "*.sh" -type f -exec chown insight:insight {} \;
RUN chown insight:insight /InsightDocker/python-client /InsightDocker/sqlite-latest.sqlite -R
RUN chown insight:insight /InsightDocker/PermissionSet.sh
RUN chmod 0600 /InsightDocker/sqlite-latest.sqlite
RUN echo "insight ALL=(root) NOPASSWD: /bin/chown -R insight\:insight /app,/bin/chmod 750 /app,/bin/chmod 0600 /app/config.ini" > /etc/sudoers.d/InsightPermissionSet
RUN chmod 0440 /etc/sudoers.d/InsightPermissionSet
USER insight
WORKDIR /app
ENTRYPOINT ["/InsightDocker/DockerEntry.sh", "python3", "/InsightDocker/Insight/Insight", "--sde-db", "/InsightDocker/sqlite-latest.sqlite"]