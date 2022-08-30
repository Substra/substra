# this base image works in both CPU and GPU enabled environments
FROM gcr.io/connect-314908/substra-tools:0.15.0-nvidiacuda11.6.0-base-ubuntu20.04-python3.9

# install dependencies
RUN pip3 install pandas numpy scikit-learn

# add your algorithm script to docker image
ADD algo.py .

# define how script is run
ENTRYPOINT ["python3", "algo.py"]
