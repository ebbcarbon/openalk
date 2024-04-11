
def test_project_imports():
    from lib.services.ph import orion_star
    from lib.services.pump import norgren
    from lib.services.titration import gran
    from lib.utils import regression
    from lib.view import gui

def test_start_ui():
    from lib.view import gui
    root = gui.App()