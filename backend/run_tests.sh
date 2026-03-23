#!/bin/bash

# Run tests for the spending tracker backend

echo "Installing test dependencies..."
pip install -r requirements.txt

echo "Running tests..."
pytest

echo "Test coverage report..."
pytest --cov=app --cov-report=html --cov-report=term-missing

echo "Tests completed!"
