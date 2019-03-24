OpenSCHC tests
==============

## Requirements

[Pytest](https://docs.pytest.org/en/latest/) is required in order to run
OpenSCHC tests. Install it using `pip`:

```
pip install pytest
```

## Run tests

Two ways to execute the test.

1. pytest framework.

In the src directory, type:
```
make pytest
```

2. a traditional way.

Move into the tests directory.

If you want to do the test with micropython, you can just type:
```
make all-tests
```

If you want to use your python, set it into the PY variable like below:
```
PY=python3 make all-tests
```

If the path is a relative path, please make the relative path from the tests directory.
```
PY=../../../micropython/ports/unix/micropython make all-tests
```
