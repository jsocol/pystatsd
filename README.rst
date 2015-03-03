======================
A Python statsd client
======================

statsd_ is a friendly front-end to Graphite_. This is a Python client
for the statsd daemon.

.. image:: https://travis-ci.org/jsocol/pystatsd.png?branch=master
   :target: https://travis-ci.org/jsocol/pystatsd
   :alt: Travis-CI build status

.. image:: https://pypip.in/v/statsd/badge.png
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Latest release

.. image:: https://pypip.in/d/statsd/badge.png
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Downloads

:Code:          https://github.com/jsocol/pystatsd
:License:       MIT; see LICENSE file
:Issues:        https://github.com/jsocol/pystatsd/issues
:Documentation: http://statsd.readthedocs.org/

Quickly, to use::

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix to all your stats::

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo')
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.

It also supports using TCP connections. Using TCP it will automatically
reconnect if the server restarts or the connection dies, all calls will
block until the message has been sent successfully::

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, proto='tcp')


Installing
==========

The easiest way to install statsd is with pip!

You can install from PyPI::

    $ pip install statsd

Or GitHub::

    $ pip install -e git+https://github.com/jsocol/pystatsd#egg=statsd

Or from source::

    $ git clone https://github.com/jsocol/pystatsd
    $ cd statsd
    $ python setup.py install


Docs
====

There are lots of docs in the ``docs/`` directory and on ReadTheDocs_.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: http://graphite.readthedocs.org/
.. _ReadTheDocs: http://statsd.readthedocs.org/en/latest/index.html
