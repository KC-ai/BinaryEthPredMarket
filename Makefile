.PHONY: all install test sim analyze clean

all: install test sim analyze

install:
	@echo "Installing dependencies..."
	npm install
	pip install -r requirements.txt

test:
	@echo "\nRunning Hardhat tests..."
	cd sim && npx hardhat test

sim:
	@echo "\nRunning market simulation..."
	node sim/sim.js

analyze:
	@echo "\nRunning analysis..."
	cd analysis && python3 multi_run.py

clean:
	@echo "Cleaning up..."
	rm -rf sim/cache sim/artifacts
	rm -f analysis/data/*.png analysis/data/*.json 