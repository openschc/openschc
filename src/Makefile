
M=../../micropython/ports/unix/micropython

all:
	@# nothing to do

style:
	pycodestyle *.py

all-tests: test-bitarray test-simsched test-oschc


test-bitarray: ; ${M} test_bitarray.py
test-simsched: ; ${M} test_simsched.py
test-oschc: ; ${M} test_oschc.py
