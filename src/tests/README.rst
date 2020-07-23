OpenSCHC tests
==============

Testing, the traditionnal way
-----------------------------

Move into the *tests* directory and run the test_xxx.py files directly.

They contain asserts, so that an unexpected result generates an error message.
Conversely, no error message on the console output means that all results are as expected.

This works with both Python3 and micropython.

You can also run::

  make all-tests

To use another version of python, such as micropython, set it into the PY variable like this::

  PY=../../../micropython/ports/unix/micropython make all-tests

If the path is a relative path, make the path relative to the *tests* directory.


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



