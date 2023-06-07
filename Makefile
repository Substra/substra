.PHONY: pyclean doc test doc-cli doc-sdk

pyclean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info

doc-sdk: pyclean
	python bin/generate_sdk_documentation.py
	python bin/generate_sdk_schemas_documentation.py
	python bin/generate_sdk_schemas_documentation.py --models --output-path='references/sdk_models.md'

doc: doc-sdk

test: pyclean
	pytest tests
