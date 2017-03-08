FROM ubuntu:16.04


RUN apt-get update \
&& apt-get install -y --no-install-recommends \
git-core ssh ca-certificates nano python virtualenv

RUN git config --global http.sslVerify true
WORKDIR /
RUN git clone https://github.com/dheeti/dlab-api
WORKDIR /dlab-api
ENV NEO4J_URI http://neo4j:neo123@54.218.68.249:7474/db/data
RUN ./setup.sh
RUN pwd
ENTRYPOINT ["./env/bin/python", "run.py"]
