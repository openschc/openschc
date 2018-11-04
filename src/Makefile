
M=../../micropython/ports/unix/micropython

all: default
	@# nothing to do

default: test-fakeschc

test-fakeschc:
	${M} test_fakeoschc.py

style:
	pycodestyle *.py

all-tests: test-bitarray test-simsched test-oschc


test-bitarray: ; ${M} test_bitarray.py
test-simsched: ; ${M} test_simsched.py
test-oschc: ; ${M} test_oschc.py
test-schcrecv: ; ${M} test_schcrecv.py
