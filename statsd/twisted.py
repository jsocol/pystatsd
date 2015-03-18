from __future__ import absolute_import

from twisted.internet import protocol

from statsd import client

class _ConnectedUDPProtocol(protocol.DatagramProtocol):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.transport = None

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def write(self, data):
        if self.transport is None:
            return
        self.transport.write(data)

class _StatsClient(client.StatsClient):

    def __init__(self, write, prefix=None, maxudpsize=512):
        self._send = write
        self._prefix = prefix
        self._maxudpsize = maxudpsize

def client(reactor=None, prefix=None, maxudpsize=512, interface='127.0.0.1', host='127.0.0.1', port=8125):
    if reactor is None:
        from twisted.internet import reactor
    protocol = _ConnectedUDPProtocol(host, port)
    reactor.listenUDP(0, protocol, interface=interface)
    write = protocol.write
    ret = _StatsClient(write, prefix=prefix, maxudpsize=maxudpsize)
    return ret
