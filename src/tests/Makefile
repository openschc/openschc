ifeq ($(PY),)
	#PY := ../../../micropython/ports/unix/micropython
	PY := micropython
endif

TESTS := $(basename $(wildcard test_*.py))
TESTBASE := __testbase__

all-tests:
	@for i in $(TESTS) ; do \
		(cat $$i.py;cat $(TESTBASE).py) | $(PY) ; \
	done
