# this base image works in both CPU and GPU enabled environments
FROM nvidia/cuda:9.0-base

# install dependencies
RUN apt-get update
RUN apt-get install -y build-essential libssl-dev python3 python3-dev python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install pandas numpy sklearn pillow scipy keras

# create base directory in which the experiment will happen
RUN mkdir -p /sandbox
RUN mkdir -p /sandbox/opener
RUN mkdir -p /sandbox/metrics
WORKDIR /sandbox

# add your algorithm script to docker image
ADD algo.py .

# define how script is run
ENTRYPOINT ["python3", "algo.py"]
