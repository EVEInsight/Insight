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

FROM python:3.6-slim-jessie
LABEL maintainer="nathan@nathan-s.com"
LABEL url="https://github.com/Nathan-LS/Insight"
ARG branch=development
WORKDIR /InsightDocker
COPY --from=SwaggerRunner /python-client ./python-client
COPY --from=SDE /sqlite-latest.sqlite ./sqlite-latest.sqlite
RUN apt-get update && apt-get install -y \
 git \
 build-essential \
 zip \
 && rm -rf /var/lib/apt/lists/*
RUN git clone -b $branch --single-branch https://github.com/Nathan-LS/Insight.git
RUN pip3 install wheel
RUN pip3 install setuptools
RUN cp /InsightDocker/python-client /InsightDocker/python-client-2 -R
WORKDIR /InsightDocker/python-client-2
RUN python3 setup.py install
WORKDIR /InsightDocker/Insight
RUN pip3 install --upgrade -r requirements.txt
RUN cp /InsightDocker/Insight/scripts/Docker/DockerEntry.sh /InsightDocker
RUN cp /InsightDocker/Insight/scripts/Docker/DockerBinBuild.sh /InsightDocker
RUN rm /InsightDocker/python-client-2 -R
RUN chmod +x /InsightDocker/DockerEntry.sh /InsightDocker/DockerBinBuild.sh
WORKDIR /app
ENTRYPOINT ["/InsightDocker/DockerEntry.sh", "python3", "/InsightDocker/Insight/Insight", "-sde", "/InsightDocker/sqlite-latest.sqlite"]