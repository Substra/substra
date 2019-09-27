# this base image works in both CPU and GPU enabled environments
FROM eu.gcr.io/substra-208412/substratools:0.0.1

# install dependencies
RUN pip3 install sklearn

# add your metrics script to docker image
ADD metrics.py .

# define how script is run
ENTRYPOINT ["python3", "metrics.py"]
