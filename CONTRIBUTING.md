## Project Structure and Style
- `lib`: top-level module. The main functionality of the package is kept here.
- `services`: main modules comprising the backend of the system, e.g. serial clients and chemistry calculations.
- `utils`: extra modules not considered to be core services.
- `view`: modules defining the desktop user interface.

Each module within these directories has a sub-directory called `tests` which stores unit tests for that module.

We generally follow [PEP8](https://peps.python.org/pep-0008/), and prefer Google-style [docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for Python code.

## Issues and Feature Requests 
If you find a bug, or want to request a new feature be added, submit these as an [issue](https://github.com/ebbcarbon/openalk/issues).

## Submitting a Pull Request
We follow a ["Gitflow"](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) development workflow, in which the `main` branch stores the latest release and the `develop` branch is used for active development.

To contribute code, follow these steps: 
- Fork the current state of the `develop` branch into your own repository 
- Name your own branch with the schema `feature/<description>`, with the description being as short as possible while still clarifying what the branch contains.
- Submit a [pull request](https://github.com/ebbcarbon/openalk/pulls) against this repository's `develop` branch from your `feature` branch.

Any changes we merge will require pytest-compatible unit tests before being incorporated. See the section below for more information.

## Unit Tests

#### Pytest
Pytest is a standard framework for unit testing in python applications. For more information about pytest, see the [pytest documentation](https://docs.pytest.org/en/8.2.x/).

See any of the `tests` sub-directories (e.g., [here](lib/services/pump/tests)) for examples of how these tests are written.

You can run the test suite yourself to see what it looks like: if on Linux, run the command `make test` from the repository's toplevel directory; if on Windows, activate the virtual environment and run the command `python -m pytest` from the same location.

#### Test Naming Requirements
* In order for your unit tests to be run, two naming conventions must be followed
    1. File names: must end with `_test.py`. Only files that end with `_test.py` will be collected and found by pytest.
        * We will follow the format of copying the name of the file to be tested and appending `_test.py` to that.
        * Example: In order to test a file named `new_feature.py`, there will be a corresponding test file named `new_feature_test.py`
    2. Test names: must start with `test_`. In order for individual test methods to be found by pytest, they must start with `test_`.
        * To test the happy path for a method named `my_method()`, you could write a test called `def test_my_method__success()`.
        * To test the sad path for that same method, you could write a test called `def test_my_method__fails()`.
