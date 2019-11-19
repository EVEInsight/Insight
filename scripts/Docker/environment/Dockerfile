FROM swaggerapi/swagger-codegen-cli:latest as SwaggerBuilder

FROM openjdk:12-jdk-alpine as SwaggerRunner
COPY --from=SwaggerBuilder /opt/swagger-codegen-cli/swagger-codegen-cli.jar ./swagger-codegen-cli.jar
RUN java -jar ./swagger-codegen-cli.jar generate \
 -i "https://esi.evetech.net/_latest/swagger.json" \
 -l python \
 -o /python-client

FROM python:3.6-slim-jessie
ARG sso_alliance_id
ARG sso_callback_url
ARG sso_char_id
ARG sso_client_id
ARG sso_corp_id
ARG sso_refresh_token
ARG sso_secret_key
WORKDIR /InsightDocker
RUN apt-get update && apt-get install -y \
 git \
 build-essential \
 zip \
 && rm -rf /var/lib/apt/lists/*
RUN pip3 install wheel
RUN pip3 install setuptools
RUN pip3 install codecov pytest-cov
COPY --from=SwaggerRunner /python-client ./python-client
WORKDIR /InsightDocker/python-client
RUN python3 setup.py install
WORKDIR /InsightDocker
COPY ./requirements.txt .
RUN pip3 install --upgrade -r requirements.txt
WORKDIR /app/Insight