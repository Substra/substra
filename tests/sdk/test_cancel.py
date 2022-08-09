from tests import mocked_requests


def test_cancel_compute_plan(client, mocker):
    m = mocked_requests.cancel_compute_plan(mocker)

    response = client.cancel_compute_plan("magic-key")

    assert response is None
    m.assert_called()
