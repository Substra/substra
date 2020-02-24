DOCKER_TAG := latest

.PHONY: pyclean doc test docker

pyclean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info

doc:
	python bin/generate_cli_documentation.py
	pydocmd simple substra.sdk+ substra.sdk.Client+ > references/sdk.md

test: pyclean
	python setup.py test

docker:
	docker build -f docker/Dockerfile . -t substra:$(DOCKER_TAG)
