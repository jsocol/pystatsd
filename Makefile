
bin/pip:
	virtualenv .

deps: bin/pip
	bin/pip install -r requirements.txt

test:	deps
	bin/python setup.py test

dist:
	bin/python setup.py dist

clean:
	- rm -rf bin lib local pip-selfcheck.json share build dist man statsd.egg-inf
	- find . -type f -name "*.pyc" -delete
	- find . -type f -name "*.pyo" -delete 
