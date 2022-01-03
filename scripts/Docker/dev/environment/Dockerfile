# build - ensure in git root of project - Sends content of ./scripts/Docker/dev/environment/ to build context.
# windows:  docker build -t insight-buildenv --no-cache --build-arg CodegenVersion="2.4.24" --build-arg PythonTag="3.6.15-buster" -f .\scripts\Docker\dev\environment\Dockerfile .\scripts\Docker\dev\environment\
# linux:    docker build -t insight-buildenv --no-cache --build-arg CodegenVersion="2.4.24" --build-arg PythonTag="3.6.15-buster" -f ./scripts/Docker/dev/environment/Dockerfile ./scripts/Docker/dev/environment/

ARG PythonTag="3.6.15-buster"

FROM openjdk:11 as SwaggerRunner
ARG CodegenVersion="2.4.25"
RUN wget https://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/$CodegenVersion/swagger-codegen-cli-$CodegenVersion.jar -O swagger-codegen-cli.jar
RUN java -jar ./swagger-codegen-cli.jar generate \
 -i "https://esi.evetech.net/_latest/swagger.json" \
 -l python \
 -o /python-client

FROM alpine:latest as SDE
RUN wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
RUN wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2.md5
RUN md5sum -c sqlite-latest.sqlite.bz2.md5
RUN bunzip2 sqlite-latest.sqlite.bz2

FROM python:$PythonTag
WORKDIR /InsightDocker
RUN apt-get update && apt-get install -y \
 git \
 build-essential \
 zip \
 && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir wheel setuptools
COPY --from=SwaggerRunner /python-client ./python-client
WORKDIR /InsightDocker/python-client
RUN python3 setup.py install
WORKDIR /InsightDocker
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
RUN pip3 install --upgrade bump2version
COPY --from=SDE /sqlite-latest.sqlite ./sqlite-latest.sqlite
WORKDIR /app/Insight
