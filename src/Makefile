#
# XXX this should be merged into the tests directory in the future.
#
ifeq ($(PY),)
	PY := micropython
	#PY := ../../micropython/ports/unix/micropython
endif

all: default
	@# nothing to do

default: test-schc

test-schc:
	${PY} test_newschc.py --data-file test/icmpv6.dmp

style:
	pycodestyle *.py

pytest:
	pytest -v

all-tests:
	@echo "Please move into the tests directory, and type make all-tests."

#test-simsched: ; ${PY} test_simsched.py
#test-oschc: ; ${PY} test_oschc.py
#test-schcrecv: ; ${PY} test_schcrecv.py
