.. _tcp-chapter:

==============
TCPStatsClient
==============

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
