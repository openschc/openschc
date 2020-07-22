OpenSCHC tests
==============

Testing, the traditionnal way
-----------------------------

It works with both micropython and Python3.

Move into the **tests** directory and run the test_xxx.py files directly.

They contain asserts, so that an unexpected result generates an error message.
Conversely, no error message on the console output means that all results are as expected.

If you want to do the test with micropython, you can just type::

  make all-tests

If you want to use your own python, set it into the PY variable like this::

  PY=python3 make all-tests

If the path is a relative path, make the path relative to the tests directory, e.g.::

  PY=../../../micropython/ports/unix/micropython make all-tests



Pytest (the modern way)
-----------------------

Installation
************

`Pytest <https://docs.pytest.org/en/latest/>`_ is required.

Install pytest with `pip`::

  pip install pytest

Run
***

In the src directory, type::

  make pytest


Guidelines
----------

If you generate new pieces of code or alter existing code, please provide/alter test code
so that they keep working both when executed with pytest and when run directly as the main.



