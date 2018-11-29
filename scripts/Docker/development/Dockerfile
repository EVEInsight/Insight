FROM maven:3-jdk-8-alpine as SwaggerBuild
RUN apk add --no-cache git
RUN git clone https://github.com/swagger-api/swagger-codegen.git
WORKDIR /swagger-codegen
RUN mvn clean package
RUN java -jar modules/swagger-codegen-cli/target/swagger-codegen-cli.jar generate \
 -i "https://esi.tech.ccp.is/_latest/swagger.json" \
 -l python \
 -o /python-client

FROM alpine:latest as SDE
RUN wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
RUN wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2.md5
RUN md5sum -c sqlite-latest.sqlite.bz2.md5
RUN bunzip2 sqlite-latest.sqlite.bz2

FROM python:3.6-slim
WORKDIR /InsightDocker
COPY --from=SwaggerBuild /python-client ./python-client
COPY --from=SDE /sqlite-latest.sqlite ./sqlite-latest.sqlite
RUN apt-get update && apt-get install -y \
 git \
 build-essential \
 && rm -rf /var/lib/apt/lists/*
RUN git clone -b experimental --single-branch https://github.com/Nathan-LS/Insight.git
RUN pip3 install wheel
RUN pip3 install setuptools
WORKDIR /InsightDocker/python-client
RUN python3 setup.py install
WORKDIR /InsightDocker/Insight
RUN rm /InsightDocker/python-client -R
RUN pip3 install --upgrade -r requirements.txt
RUN cp /InsightDocker/Insight/scripts/Docker/DockerEntry.sh /InsightDocker
RUN chmod +x /InsightDocker/DockerEntry.sh
WORKDIR /app
ENTRYPOINT ["/InsightDocker/DockerEntry.sh", "python3", "/InsightDocker/Insight/Insight", "-sde", "/InsightDocker/sqlite-latest.sqlite"]