# this base image works in both CPU and GPU enabled environments
FROM substrafoundation/substra-tools:0.5.0

# install dependencies
RUN pip3 install pandas numpy sklearn pillow scipy keras

# add your algorithm script to docker image
ADD algo.py .

# define how script is run
ENTRYPOINT ["python3", "algo.py"]
