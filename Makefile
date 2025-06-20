#!/usr/bin/make -f

# Portions of this file contributed by NIST are governed by the
# following statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to Title 17 Section 105 of the
# United States Code, this software is not subject to copyright
# protection within the United States. NIST assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL := /bin/bash

all: \
  check-examples
	source venv/bin/activate \
	  && case_viewer \
	    examples/WirelessNetworkConnection.json

.PHONY: \
  check-examples

.dry_run.done.log: \
  .pytest.done.log
	source venv/bin/activate \
	  && case_viewer \
	    --dry-run \
	    examples/WirelessNetworkConnection.json
	touch $@

.mypy_strict.done.log: \
  .venv.done.log \
  case_viewer/lib.py
	source venv/bin/activate \
	  && poetry run mypy \
	    --strict \
	    case_viewer/lib.py
	touch $@

.mypy.done.log: \
  .mypy_strict.done.log \
  case_viewer/case_viewer.py
	source venv/bin/activate \
	  && poetry run mypy \
	    case_viewer/case_viewer.py
	touch $@

.pytest.done.log: \
  .mypy.done.log
	source venv/bin/activate \
	  && poetry run pytest \
	    --doctest-modules \
	    case_viewer/lib.py
	touch $@

.venv.done.log: \
  pyproject.toml
	rm -f poetry.lock
	rm -rf venv
	python3 -m venv venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    poetry
	source venv/bin/activate \
	  && poetry install \
	    --with dev
	touch $@

check: \
  .dry_run.done.log \
  check-examples

check-examples: \
  .venv.done.log
	$(MAKE) \
	  --directory examples \
	  check

clean:
	@$(MAKE) \
	  --director examples \
	  clean
	@rm -f \
	  .*.done.log
	@rm -rf \
	  venv
