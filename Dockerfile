FROM python:3.11-slim-bullseye

WORKDIR /

RUN apt-get update && apt-get install -y \
    sane \
    sane-utils \
    libsane-dev \
    ipp-usb \
    gcc \
    git \
    sane-airscan \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

#RUN git clone --depth 1 --branch main https://github.com/thartman83/archivist-descry.git /app
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /app

ENV APPCONFIG PROD

CMD [ "/bin/bash", "-c", "/etc/init.d/dbus start;python /app/run.py" ]
