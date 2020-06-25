.PHONY: pyclean doc test

pyclean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info

doc-cli:
	python bin/generate_cli_documentation.py

doc-sdk:
	pydocmd simple substra.sdk+ substra.sdk.Client+ > references/sdk.md

doc: doc-cli doc-sdk

test: pyclean
	python setup.py test
