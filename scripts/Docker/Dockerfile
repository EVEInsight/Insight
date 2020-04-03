FROM swaggerapi/swagger-codegen-cli:latest as SwaggerBuilder

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

FROM python:3.6-slim-stretch
LABEL maintainer="nathan@nathan-s.com"
LABEL url="https://github.com/Nathan-LS/Insight"
ARG INSIGHT_BRANCH=master
ARG INSIGHT_REPO=https://github.com/Nathan-LS/Insight.git

ENV SQLITE_DB_PATH="Database.db"
ENV HEADERS_FROM_EMAIL=""
ENV DISCORD_TOKEN=""
ENV CCP_CLIENT_ID=""
ENV CCP_SECRET_KEY=""
ENV CCP_CALLBACK_URL=""
ENV DISCORDBOTS_APIKEY=""

RUN apt-get update && apt-get install -y \
 git \
 build-essential \
 zip \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /InsightDocker /app /home/insight
RUN addgroup -gid 1007 insight
RUN useradd --system --shell /bin/bash --home /app -u 1006 -g insight insight
RUN chown insight:insight /InsightDocker /app /home/insight
USER insight
WORKDIR /InsightDocker
COPY --from=SwaggerRunner /python-client ./python-client
COPY --from=SDE /sqlite-latest.sqlite ./sqlite-latest.sqlite
RUN git clone -b $INSIGHT_BRANCH --single-branch $INSIGHT_REPO
RUN cp /InsightDocker/python-client /InsightDocker/python-client-2 -R
USER root
RUN pip3 install wheel setuptools
WORKDIR /InsightDocker/python-client-2
RUN python3 setup.py install
WORKDIR /InsightDocker/Insight
RUN pip3 install --upgrade -r requirements.txt
RUN find /InsightDocker/Insight/scripts/Docker/ -maxdepth 1 -name "*.sh" -type f -exec cp {} /InsightDocker/ \;
RUN rm /InsightDocker/python-client-2 -R
RUN find /InsightDocker/ -maxdepth 1 -name "*.sh" -type f -exec chmod 500 {} \;
RUN find /InsightDocker/ -maxdepth 1 -name "*.sh" -type f -exec chown insight:insight {} \;
RUN chown insight:insight /InsightDocker/python-client /InsightDocker/sqlite-latest.sqlite -R
RUN chmod 600 /InsightDocker/sqlite-latest.sqlite
WORKDIR /app
ENTRYPOINT ["/InsightDocker/DockerEntry.sh", "python3", "/InsightDocker/Insight/Insight", "-sde", "/InsightDocker/sqlite-latest.sqlite"]