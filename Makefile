.PHONY: pyclean doc test

pyclean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info

doc-cli:
	python bin/generate_cli_documentation.py

doc-sdk:
	sphinx-build -M markdown src-references _build -c .
	cp _build/markdown/sdk.md references/

doc: doc-cli doc-sdk

test: pyclean
	python setup.py test
