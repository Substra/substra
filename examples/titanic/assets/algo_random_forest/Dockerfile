# this base image works in both CPU and GPU enabled environments
FROM gcr.io/connect-314908/connect-tools:0.8.0

# install dependencies
RUN pip3 install pandas numpy 'scikit-learn==0.24.2' pillow scipy keras

# add your algorithm script to docker image
ADD algo.py .

# define how script is run
ENTRYPOINT ["python3", "algo.py"]
