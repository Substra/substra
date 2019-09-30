ALGO = 'algo'
DATA_SAMPLE = 'data_sample'
DATASET = 'dataset'
MODEL = 'model'
OBJECTIVE = 'objective'
TESTTUPLE = 'testtuple'
TRAINTUPLE = 'traintuple'
COMPUTE_PLAN = 'compute_plan'
NODE = 'node'

_SERVER_MAPPER = {
    DATASET: 'data_manager',
}


def get_all():
    return (
        ALGO,
        DATA_SAMPLE,
        DATASET,
        MODEL,
        OBJECTIVE,
        TESTTUPLE,
        TRAINTUPLE,
        COMPUTE_PLAN,
        NODE,
    )


def to_server_name(asset):
    try:
        return _SERVER_MAPPER[asset]
    except KeyError:
        return asset
