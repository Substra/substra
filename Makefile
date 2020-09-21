.PHONY: pyclean doc test

pyclean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info

doc-cli:
	python bin/generate_cli_documentation.py

doc-sdk:
	pydocmd simple substra.sdk+ substra.sdk.Client+ substra.sdk.retry_on_exception+ > references/sdk.md

doc-schemas:
	python bin/generate_sdk_schemas_documentation.py
	python bin/generate_sdk_schemas_documentation.py --models --output-path='references/sdk_models.md'

doc: doc-cli doc-sdk doc-schemas

test: pyclean
	python setup.py test
