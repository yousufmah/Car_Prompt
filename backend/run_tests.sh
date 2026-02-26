#!/bin/bash
# Run tests for CarPrompt API

echo "Installing test dependencies..."
pip install -r requirements-test.txt

echo "Running tests..."
pytest tests/ -v --tb=short

echo "Test coverage report..."
pytest tests/ --cov=app --cov-report=term-missing