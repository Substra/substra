ALGO = 'algo'
DATA_SAMPLE = 'data_sample'
DATASET = 'dataset'
MODEL = 'model'
OBJECTIVE = 'objective'
TESTTUPLE = 'testuple'
TRAINTUPLE = 'traintuple'

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
    )


def to_server_name(asset):
    try:
        return _SERVER_MAPPER[asset]
    except KeyError:
        return asset
