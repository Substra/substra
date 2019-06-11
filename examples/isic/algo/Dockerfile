# this base image works in both CPU and GPU enabled environments
# to pull this image from our private registry you need to be authenticated using your google account
FROM eu.gcr.io/substra-208412/substratools

# install dependencies
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
