import substra


def test_client_tmp_dir():
    """Test the creation of a temp directory for the debug client"""
    client = substra.Client(debug=True)
    assert client.temp_directory


def test_client_multi_nodes_dataset(dataset_query):
    """Assert that the owner is gotten from the metadata in debug mode"""
    client = substra.Client(debug=True)
    dataset_query['metadata'] = {substra.DEBUG_OWNER: 'owner_1'}

    key = client.add_dataset(dataset_query)
    asset = client.get_dataset(key)
    assert asset.owner == 'owner_1'
