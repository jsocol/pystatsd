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



# Install

The easiest way to install statsd is with pip!

You can install from PyPI:

```bash
pip install statshog
```

Or GitHub:

```bash
$ pip install -e git+https://github.com/macobo/statshog#egg=statshog
```

Or from source:

```bash
git clone https://github.com/macobo/statshog
cd pystatsd
python setup.py install
```

# Usage

## Quick usage

```python
import statshog
statsd = statshog.StatsClient(host='localhost', port=8125)
statsd.incr('foo')  # Increment the 'foo' counter.
statsd.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'
```

## Using with telegraf/influxdb

```python
import statshog
statsd = statshog.StatsClient(telegraf=True)
statsd.timing('stats.timed', 320, tags={"mytag": 456})
```

## django-statsd

To use together with
[django-statsd](<https://github.com/django-statsd/django-statsd>), add
the following to your `settings.py`:

```
STATSD_CLIENT = "statshog"
```
