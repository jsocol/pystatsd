.. _unix-socket-chapter:

=====================
UnixSocketStatsClient
=====================

The ``UnixSocketStatsClient`` class has a very similar interface to
``TCPStatsClient``, but internally it uses Unix Domain sockets instead of TCP.
These are the main differencies when using ``TCPStatsClient`` compared
to ``UnixSocketStatsClient``:

* Instead of host and port params UnixStatsSocket constructor accepts only socket_path and there is no default value for it.

* There is not ``ipv6`` parameter in constructor.

* You need to make sure that you have correct permissions to write to provided socket.
