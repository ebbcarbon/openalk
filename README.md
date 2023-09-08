# ta_autotitrator
## Unit Tests
Each service/utils directory should have a `tests` sub-directory. Within this `tests` sub-directory, there should be multiple unit test files corresponding to their services.

ALL new pull requests and logic changes should come with unit tests to confirm these changes work. Development work is NOT complete without unit tests.

#### Running test suite
To run all unit tests (that are named correctly in correspondence with the naming requirements outlined below), simply run `pytest` command from the base directory in your terminal.

#### Test Naming Requirements
* In order for your unit tests to be run, two naming conventions MUST be followed
    1. File names: MUST END with `_test.py`. Only files that end with `_test.py` will be collected and found by pytest.
        * We will follow the format of copying the file to be tested's name and appending `_test.py` to that.
        * Example: In order to test a file named `my_service_file.py`, there will be a corresponding test file named `my_service_file_test.py`
    2. Test names: MUST START with `test_`. In order for individual test methods to be found by pytest, they must start with `test_`.
        * To test the happy path for a method named `my_method()`, you could write a test called `def test_my_method__success()`.
        * To test the sad path for that same method, you could write a test called `def test_my_method__fails()`.