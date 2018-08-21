.. _unix-socket-chapter:

=====================
UnixSocketStatsClient
=====================

.. py:class:: UnixSocketStatsClient(socket_path, prefix=None, timeout=None)

   :param string socket_path: The path to the Unix socket
   :param prefix: The stat name prefix
   :type prefix: str or None
   :param timeout: The TCP socket timeout
   :type timeout: number or None

.. code-block:: python

    statsd = UnixSocketStatsClient(socket_path='/var/run/stats.sock')

The ``UnixSocketStatsClient`` class has a very similar interface to
``TCPStatsClient``, but internally it uses Unix Domain sockets instead
of TCP.  These are the main differences when using
``UnixSocketStatsClient`` compared to ``StatsClient``:

* The ``socket_path`` parameter is required. It has no default.

* The ``host``, ``port`` and ``ipv6`` parameters are not allowed.

* The application process must have permission to write to the socket.
