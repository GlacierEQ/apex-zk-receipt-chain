.PHONY: test verify lint lean-check

test:
	python3 -m pytest tests/ -v

verify:
	python3 src/prover.py verify

lint:
	python3 -m py_compile src/*.py

lean-check:
	echo "Lean check (stubbed)"
