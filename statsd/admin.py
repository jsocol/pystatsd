
import socket
import simplejson as json


class StatsdAdminClient(object):
    """
    A client for statsd admin interface.
    Example commands: stats, counters, timers, gauges, delcounters, deltimers, delgauges, quit


    Usage:
       statsd_admin = StatsdAdminClient('mystatshost')
       gauges = statsd_admin.list('gauges')
       for gauge, value in gauges.items():
           print "%s = %r" % (gauge, value)

       statsd_admin.del_gauges(['foo.bar.baz', 'foo.bar.qux'])
    """

    def __init__(self, host='localhost', port=8126):
        """Create a new client."""
        self.rbufsize = -1
        self._addr = (socket.gethostbyname(host), port)

    def list(self, stat_type='stats'):
        """
        Returns a dictionary of stat:value pairs for all stats that statsd
        is tracking.
        stat_type could be one of:  stats, counters, timers, gauges
        """
        sock = socket.socket(socket.AF_INET)
        sock.connect(self._addr)
        sock.send(stat_type + "\n")
        # Open a file-like object for this socket and read it to 'txt'
        rfile = sock.makefile('r', self.rbufsize)
        txt = ""
        for line in rfile:
            if line == "END\n":
                break
            if line:
                txt += line.replace("'", "\"")
        sock.close()

        if txt[0] == '{':
            data = json.loads(txt)
        else:
            data = {}
            for line in txt.split("\n"):
                if ":" in line:
                    key, val = line.split(":")
                    key = key.strip()
                    val = val.strip()
                    data[key] = val # Not converting to numbers
        return data

    def del_gauges(self, gauges):
        """
        Delete the given gauges from statsd.
        gauges is a list of gauge keys.
        If statsd receives more data for a deleted gauge, it will be recreated.
        """
        sock = socket.socket(socket.AF_INET)
        sock.connect(self._addr)
        msg = "delgauges " + " ".join(gauges)
        sock.send(msg + "\n")
        sock.close()

    def del_timers(self, timers):
        """
        Delete the given timers from statsd.
        If statsd receives more data for a deleted timer, it will be recreated.
        """
        sock = socket.socket(socket.AF_INET)
        sock.connect(self._addr)
        msg = "deltimers " + " ".join(timers)
        sock.send(msg + "\n")
        sock.close()

    def del_counters(self, counters):
        """
        Delete the given counters from statsd.
        If statsd receives more data for a deleted counter, it will be recreated.
        """
        sock = socket.socket(socket.AF_INET)
        sock.connect(self._addr)
        msg = "delcounters " + " ".join(counters)
        sock.send(msg + "\n")
        sock.close()
