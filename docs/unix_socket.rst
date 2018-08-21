.. _unix-socket-chapter:

=====================
UnixSocketStatsClient
=====================

.. code-block:: python

    statsd = UnixSocketStatsClient(socket_path='/var/run/stats.sock')

The :py:class:`UnixSocketStatsClient` class has a very similar interface to
:py:class:`TCPStatsClient`, but internally it uses Unix Domain sockets instead
of TCP.  These are the main differences when using ``UnixSocketStatsClient``
compared to ``StatsClient``:

* The ``socket_path`` parameter is required. It has no default.

* The ``host``, ``port`` and ``ipv6`` parameters are not allowed.

* The application process must have permission to write to the socket.
