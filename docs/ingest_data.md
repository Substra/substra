# Ingest data samples to Substra

Data samples should be ingested to Substra using our python SDK or our command line
interface tool.

2 different modes are available when adding data samples:
- local: data are located on the local filesystem and are transferred through HTTP
  requests. This mode is most likely to be used to add relatively small files or for
  testing purposes.
- remote: data are located on the server filesystem. Data must have been transferred
  previously to the server. This mode is recommended for adding relatively big data 
  samples or for adding many data samples.
