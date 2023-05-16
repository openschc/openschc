What is OpenSCHC ?
===================

OpenSCHC
--------

OpenSCHC is an open-source implementation of SCHC (Static Context Header Compression) standardized at the IETF by the `LPWAN Working Group <https://tools.ietf.org/wg/lpwan/>`_ as `RFC8724 <https://www.rfc-editor.org/info/rfc8724>`_.
Oversimplifying, this is essentially IP protocol header compression and fragmentation so that they can be transported by low datarate, long range IoT networks.

The long-term goal is to have a stable, open-source, reference Python3 codebase for the SCHC protocol.

.. OpenSCHC is developed to be compatible with MicroPython, on the device side.

OpenSCHC is licensed under the `MIT License <https://github.com/openschc/openschc/blob/master/LICENSE>`_.

Project Documentation
=====================

The full documentation about OpenSCHC is available 
`here <https://openschc.github.io/openschc>`_ .

run from source
===============

- `pip install -r requirements.txt`
- `python -m openschc`

build
=====

- `pip install --upgrade pip setuptools build`
- `python -m build`

install locally
===============

- `pip install .`

After installation, verify you can the `openschc` commmand from any directory.

uninstall locally
=================

- `pip uninstall openschc`

After installation, verify you can no longer run the `openschc` commmand.

upload to PyPI
==============

- create an API token after logging in at https://pypi.org/ (it's a long string starting with `pypi-`)
- `pip install --upgrade twine`
- `twine upload dist/*`
    - username: `__token__`
    - password: the entire token above, including the `pypi-` prefix
- update appears at https://pypi.org/project/openschc/
