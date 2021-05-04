A Python statsd client
======================

A python client for [Etsy](<http://etsy.com>)'s
[StatsD](<https://github.com/etsy/statsd>) server and
[InfluxDB's](<http://influxdb.com>)
[Telegraf](<https://github.com/influxdb/telegraf>) StatsD server.

[![Latest release](https://img.shields.io/pypi/v/statshog.svg)](https://pypi.python.org/pypi/statshog/)

[![Supported Python versions](https://img.shields.io/pypi/pyversions/statshog.svg)](https://pypi.python.org/pypi/statshog/)

[![Wheel Status](https://img.shields.io/pypi/wheel/statshog.svg)](https://pypi.python.org/pypi/statshog/)

Code:   <https://github.com/macobo/statshog>

License:   MIT; see LICENSE file

Issues:   <https://github.com/macobo/statshog/issues>

Documentation:   <https://statshog.readthedocs.io/>

Quickly, to use:

```python
>>> import statshog
>>> c = statshog.StatsClient('localhost', 8125)
>>> c.incr('foo')  # Increment the 'foo' counter.
>>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.
```

You can also add a prefix to all your stats:

```python
>>> import statshog
>>> c = statshog.StatsClient('localhost', 8125, prefix='foo')
>>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.
```

# Installing

The easiest way to install statsd is with pip!

You can install from PyPI:

    $ pip install statsd

Or GitHub:

```
$ pip install -e git+https://github.com/macobo/statshog#egg=statshog
```

Or from source:

```bash
$ git clone https://github.com/macobo/statshog
$ cd pystatsd
$ python setup.py install
```

To use together with
[django-statsd](<https://github.com/django-statsd/django-statsd>), add
the following to your `settings.py`:

```
STATSD_CLIENT = "statshog"
```

# Docs

There are lots of docs in the docs/\` directory and on
[ReadTheDocs](https://statsd.readthedocs.io/en/latest/index.html).
