FROM nvidia/cuda:9.0-base

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev python3 python3-dev python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install pandas numpy sklearn pillow

RUN mkdir -p /sandbox
RUN mkdir -p /sandbox/opener
RUN mkdir -p /sandbox/metrics

WORKDIR /sandbox

ADD ./calc_metrics.py .

ENTRYPOINT ["python3", "calc_metrics.py"]
