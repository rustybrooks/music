FROM ubuntu:18.04

RUN apt-get -y update \
 && DEBIAN_FRONTEND=noninteractive apt-get -yq install curl apt-utils sudo nano build-essential git \
 python python-pip python-numpy \
 libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg \
 && rm -rf /var/cache/apt/archives/*

#RUN git clone https://git.aubio.org/aubio/aubio \
# && cd aubio \
# && make \
# && pip3 install .

RUN mkdir -p /srv/src

ENTRYPOINT /srv/src/audio_to_midi/entrypoint.sh
WORKDIR /srv/src/audio_to_midi

## stuff that changes after here
COPY . /srv/src/
RUN pip install -r /srv/src/audio_to_midi/requirements.txt

