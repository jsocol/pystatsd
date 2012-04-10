.. _configuring-chapter:

==================
Configuring Statsd
==================

It's easy to configure and use Statsd at runtime, but there are also two
shortcuts available.


Runtime
=======

If you are running the statsd_ server locally and on the default port, it's
extremely easy::

    from statsd import StatsClient

    statsd = StatsClient()
    statsd.incr('foo')

There are three arguments to configure your ``StatsClient`` instance. They, and
their defaults, are::

    from statsd import StatsClient

    statsd = StatsClient(host='localhost',
                         port=8125,
                         prefix=None)

``host`` is the host running the statsd server. It will support any kind of
name or IP address you might use.

``port`` is the statsd server port. The default for both server and client is
``8125``.

``prefix`` helps distinguish multiple applications or environments using the
same statsd server. It will be prepended to all stats, automatically. For
example::

    from statsd import StatsClient

    foo_stats = StatsClient(prefix='foo')
    bar_stats = StatsClient(prefix='bar')

    foo_stats.incr('baz')
    bar_stats.incr('baz')

will produce two different stats, ``foo.baz`` and ``bar.baz``. Without the
``prefix`` argument, or with the same ``prefix``, two ``StatsClient`` instances
will update the same stats.


In Django
=========

If you are using Statsd in a Django_ application, you can configure a default
``StatsClient`` in the Django settings. All of these settings are optional.

Here are the settings and their defaults::

    STATSD_HOST = 'localhost'
    STATSD_PORT = 8125
    STATSD_PREFIX = None

You can use the default ``StatsClient`` simply::

    from statsd import statsd

    statsd.incr('foo')

This instance will use the settings, if provided by Django. If no Django
settings can be imported, it won't be available.


From the Environment
====================

Statsd isn't only useful in Django or on the web. A default instance will also
be available if you configure at least two environment variables. These do not
have defaults.

You can set these variables in the environment::

    STATSD_HOST
    STATSD_PORT
    STATSD_PREFIX

and then in your Python application, you can simply do::

    from statsd import statsd

    stats.incr('foo')

**NB**: To make this default instance available, you will need to set at least
``STATSD_HOST`` and ``STATSD_PORT``, even if using the default values of
``localhost`` and ``8125``.

.. _statsd: https://github.com/etsy/statsd
.. _Django: https://www.djangoproject.com/
