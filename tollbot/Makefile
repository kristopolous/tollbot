# Tollbot Makefile

.PHONY: build test lint install clean

build:
	pip install -e .

test:
	python3 -m pytest tollbot/tests/ -v

lint:
	@echo "Running linter..."
	black --check tollbot/src/tollbot/ || true
	flake8 tollbot/src/tollbot/ || true

install:
	pip install -e .
	sudo cp tollbot/src/tollbot/cli/main.py /usr/local/bin/tollbot 2>/dev/null || echo "Install manually or use pip"

clean:
	rm -rf tollbot/build tollbot/dist tollbot/*.egg-info
	rm -rf tollbot/src/tollbot/__pycache__
