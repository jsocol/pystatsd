import random
import re

import mock
from nose.tools import eq_

from statsd import StatsClient


ADDR = ('localhost', 8125)



def _client(prefix=None):
    sc = StatsClient(host=ADDR[0], port=ADDR[1], prefix=prefix)
    sc._sock = mock.Mock()
    return sc


def _sock_check(cl, count, val):
    eq_(cl._sock.sendto.call_count, count)
    eq_(cl._sock.sendto.call_args, ((val, ADDR), {}))


@mock.patch.object(random, 'random', lambda: -1)
def test_incr():
    sc = _client()

    sc.incr('foo')
    _sock_check(sc, 1, 'foo:1|c')

    sc.incr('foo', 10)
    _sock_check(sc, 2, 'foo:10|c')

    sc.incr('foo', 10, rate=0.5)
    _sock_check(sc, 3, 'foo:10|c|@0.5')


@mock.patch.object(random, 'random', lambda: -1)
def test_decr():
    sc = _client()

    sc.decr('foo')
    _sock_check(sc, 1, 'foo:-1|c')

    sc.decr('foo', 10)
    _sock_check(sc, 2, 'foo:-10|c')


@mock.patch.object(random, 'random', lambda: -1)
def test_timing():
    sc = _client()

    sc.timing('foo', 100)
    _sock_check(sc, 1, 'foo:100|ms')

    sc.timing('foo', 350)
    _sock_check(sc, 2, 'foo:350|ms')

    sc.timing('foo', 100, rate=0.5)
    _sock_check(sc, 3, 'foo:100|ms|@0.5')


def test_prefix():
    sc = _client('foo')

    sc.incr('bar')
    _sock_check(sc, 1, 'foo.bar:1|c')


def _timer_check(cl, count, start, end):
    eq_(cl._sock.sendto.call_count, count)
    value = cl._sock.sendto.call_args[0][0]
    exp = re.compile('^%s:\d+|%s$' % (start, end))
    assert exp.match(value)


def test_timer():
    """StatsClient.timer is a context decorator."""
    sc = _client()

    with sc.timer('foo'):
        pass

    _timer_check(sc, 1, 'foo', 'ms')

    @sc.timer('bar')
    def bar():
        pass

    bar()

    _timer_check(sc, 2, 'bar', 'ms')


def test_timer_capture():
    """You can capture the output of StatsClient.timer."""
    sc = _client()
    with sc.timer('woo') as result:
        eq_(result.ms, None)
    assert isinstance(result.ms, int)


@mock.patch.object(random, 'random', lambda: -1)
def test_timer_rate():
    sc = _client()

    with sc.timer('foo', rate=0.5):
        pass

    _timer_check(sc, 1, 'foo', 'ms|@0.5')

    @sc.timer('bar', rate=0.1)
    def bar():
        pass

    bar()

    _timer_check(sc, 2, 'bar', 'ms|@0.1')
