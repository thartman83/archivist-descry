FROM python:3.11-alpine

WORKDIR /app

#RUN apt-get update && apt-get install -y \
#    sane \
#    sane-utils \
#    libsane-dev \
#    gcc \
#    git \
#    sane-airscan \
#    && rm -rf /var/lib/apt/lists/*

RUN apk add --no-cache sane sane-utils gcc git sane-dev

RUN git clone --depth 1 --branch 0.99.27 https://github.com/alexpevzner/sane-airscan.git sane-airscan

RUN cd sane-airscan
RUN make ./
RUN make install

RUN cd ..
RUN git clone --depth 1 --branch main https://github.com/thartman83/archivist-descry.git descry

RUN pip3 install -r descry/requirements.txt
CMD [ "python3", "descry/app/run.py"]
