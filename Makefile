.PHONY: test
test:
	nose2 statsd --with-coverage

.PHONY: tox
tox:
	tox

.PHONY: release
release: build check
	twine upload --non-interactive --sign dist/*

.PHONY: clean
clean:
	rm -rf dist

.PHONY: build
build: clean
	python -m build


.PHONY: check
check:
	twine check dist/*
