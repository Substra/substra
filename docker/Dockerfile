FROM python:3.7

RUN pip3 install keyrings.alt

RUN mkdir -p /usr/src/app/substra
COPY ./requirements.txt /usr/src/app/substra/
COPY ./substra/ /usr/src/app/substra/substra/
COPY ./setup.* /usr/src/app/substra/
COPY ./README.md /usr/src/app/substra/
RUN pip3 install -e /usr/src/app/substra

WORKDIR /usr/src/app
