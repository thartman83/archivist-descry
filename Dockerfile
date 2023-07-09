FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    sane \
    sane-utils \
    libsane-dev \
    gcc \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://download.brother.com/welcome/dlf105200/brscan4-0.4.11-1.amd64.deb > brscan4-0.4.11-1.amd64.deb
RUN dpkg -i --force-all brscan4-0.4.11-1.amd64.deb
RUN /opt/brother/scanner/brscan4/brsaneconfig4 -a name="BROTHER_MFC-L2700DW" model="MFC-L2700DW" ip="172.17.1.28"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "run.py"]
