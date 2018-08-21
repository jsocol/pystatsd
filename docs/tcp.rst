.. _tcp-chapter:

==============
TCPStatsClient
==============

.. py:class:: TCPStatsClient(host='localhost', port=8125, prefix=None, timeout=None, ipv6=False)

   :param str host: The hostname of the StatsD server
   :param int port: The port number of the StatsD server
   :param prefix: The stat name prefix
   :type prefix: str or None
   :param timeout: The TCP socket timeout
   :type timeout: number or None
   :param bool ipv6: Use IPv6 for server name resolution

.. code-block:: python

    statsd = TCPStatsClient(host='1.2.3.4', port=8126, timeout=1.)

The ``TCPStatsClient`` class has a very similar interface to
``StatsClient``, but internally it uses TCP connections instead of UDP.
These are the main differencies when using ``TCPStatsClient`` compared
to ``StatsClient``:

* The constructor supports a ``timeout`` parameter to set a timeout on
  all socket actions.

* ``connect()`` and all methods that send data can potentially raise
  socket exceptions.

* **It is not thread-safe**, so it is recommended to not share it across
  threads unless a lot of attention is paid to make sure that no two
  threads ever use it at once.
