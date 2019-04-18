FROM substra/substratools

RUN mkdir -p /sandbox
RUN mkdir -p /sandbox/opener
RUN mkdir -p /sandbox/metrics
WORKDIR /sandbox

ENTRYPOINT ["python3"]
CMD ["-c", "import substratools as tools; tools.metrics.execute()"]
