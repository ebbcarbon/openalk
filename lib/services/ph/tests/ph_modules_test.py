# Write unit tests for ph_modules logic here
# Tests MUST start with `test_` for pytest to find them

from unittest.mock import patch

from lib.services.ph.ph_modules import pH_meter_simulated


@patch.object(pH_meter_simulated, "read_emf_pH")
def test_ph_simulated_module(mock_read_emf_ph):
    """
    Dummy test demonstrating mocking.
    TODO: Replace this with actual unit test logic.
    """
    mock_read_emf_ph.return_value = "banana"

    result = pH_meter_simulated().read_emf_pH()
    assert result == "banana"
