Testing information
*******************

With Python3, we use pytest.
See Readme.md under src/tests.

The old way works with both micropython and Python3:
from the src directory, just execute the tests/test_xxxx.py files one by one.
They contain asserts, so that an unexpected results generates an error message.
Conversely, no error message on the console output means that all results are as expected.


If you generate new pieces of code or alter existing code, please provide/alter test code
working both when executed with pytest and when run as main.

Quick links
===========

===================== ======================================================================
Resource
===================== ======================================================================
pytest repo           https://pytest.org
===================== ======================================================================

