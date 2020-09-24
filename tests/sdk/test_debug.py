
import substra


def test_client_tmp_dir():
    client = substra.Client(debug=True)
    assert client.temp_directory
