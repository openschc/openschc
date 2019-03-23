
M=../../micropython/ports/unix/micropython

all: default
	@# nothing to do

default: test-oschc

test-oschc:
	${M} test_newschc.py

style:
	pycodestyle *.py

all-tests: test-bitarray test-simsched test-oschc

pytest:
	pytest -v

test-bitarray: ; ${M} test_bitarray.py
test-simsched: ; ${M} test_simsched.py
test-oschc: ; ${M} test_oschc.py
test-schcrecv: ; ${M} test_schcrecv.py
