# Write unit tests for titration logic here
# Tests MUST start with `test_` for pytest to find them

from unittest.mock import patch

from lib.services.titration.titration_class import Titration


@patch.object(Titration, "requiredVol")
def test_titration_method_1(mock_required_vol):
    """
    This is a fake test demonstrating mocking.
    TODO: Replace this with actual logical unit tests.
    """
    mock_required_vol.return_value = 4
    # Parameter inputs here are dummy inputs
    assert Titration(sampleSize=1, S=2, T=3, pHs=4, emf=5, volumeAdded=6).requiredVol(Cacid=7, pHf=8) == 4
