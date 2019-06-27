COMPILED_PROTOS	:= tests/functional/domain_pb2.py tests/functional/domain_pb2_grpc.py
default: dependencies tests docs

dependencies:
	pipenv install --dev

develop:
	pipenv run python setup.py develop

tests: proto
	pipenv run nosetests --cover-erase --with-watch tests

unit:
	pipenv run nosetests tests/unit --cover-erase # let's clear the test coverage report during unit tests only


$(COMPILED_PROTOS):
	pipenv run python -m grpc_tools.protoc -I tests/functional/ --python_out=tests/functional/ --grpc_python_out=tests/functional/ tests/functional/*.proto

proto: $(COMPILED_PROTOS)

functional: proto
	pipenv run nosetests tests/functional

docs:
	cd docs && pipenv run make html

release:
	@rm -rf dist/*
	@./.release
	@make pypi
	@git push
	@git push --tags

pypi:
	@pipenv run python setup.py build sdist
	@pipenv run twine check dist/*.tar.gz
	@pipenv run twine upload dist/*.tar.gz

clean:
	@rm -rfv $(COMPILED_PROTOS)
	@find . -type f -name '*.pyc' -exec rm -fv {} \;
	@rm -rfv docs/build dist *egg-info*

.PHONY: docs tests
