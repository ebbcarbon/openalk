
def test_project_imports():
    """Test all the major project modules can be imported
    successfully.
    """
    from lib.services.ph import orion_star
    from lib.services.pump import norgren
    from lib.services.titration import gran
    from lib.utils import regression
    from lib.view import gui