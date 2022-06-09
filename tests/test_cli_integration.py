"""
    Test the cli and its call to the sdk. Mock the backend instead of the sdk.
    """


from tests import mocked_requests
from tests.test_cli import client_execute


def test_cancel_compute_plan(workdir, mocker):
    m = mocked_requests.cancel_compute_plan(mocker)
    client_execute(workdir, ["cancel", "compute_plan", "fakekey"])
    m.assert_called()
