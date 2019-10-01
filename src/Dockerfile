FROM ubuntu:18.04

RUN apt-get -y update \
 && apt-get install -y sudo \
                       build-essential \
                       python3 \
                       python3-pip curl \
  && pip3 install --upgrade pip

RUN pip3 install PyMySQL

COPY requirements.txt /srv
COPY playerdb/requirements.txt /srv/playerdb_requirements.txt
COPY webapi/requirements.txt /srv/webapi_requirements.txt
RUN pip3 install -r /srv/requirements.txt -r /srv/playerdb_requirements.txt -r /srv/webapi_requirements.txt



