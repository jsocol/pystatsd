from __future__ import with_statement
import random
import re
import socket

import mock
from nose.tools import eq_

from statsd import StatsClient


ADDR = (socket.gethostbyname('localhost'), 8125)


def _client(prefix=None):
    sc = StatsClient(host=ADDR[0], port=ADDR[1], prefix=prefix)
    sc._sock = mock.Mock()
    return sc


def _sock_check(cl, count, val=None):
    eq_(cl._sock.sendto.call_count, count)
    if val is not None:
        val = val.encode('ascii')
        eq_(cl._sock.sendto.call_args, ((val, ADDR), {}))


class assert_raises(object):
    """A context manager that asserts a given exception was raised.

    >>> with assert_raises(TypeError):
    ...     raise TypeError

    >>> with assert_raises(TypeError):
    ...     raise ValueError
    AssertionError: ValueError not in ['TypeError']

    >>> with assert_raises(TypeError):
    ...     pass
    AssertionError: No exception raised.

    Or you can specify any of a number of exceptions:

    >>> with assert_raises(TypeError, ValueError):
    ...     raise ValueError

    >>> with assert_raises(TypeError, ValueError):
    ...     raise KeyError
    AssertionError: KeyError not in ['TypeError', 'ValueError']

    You can also get the exception back later:

    >>> with assert_raises(TypeError) as cm:
    ...     raise TypeError('bad type!')
    >>> cm.exception
    TypeError('bad type!')
    >>> cm.exc_type
    TypeError
    >>> cm.traceback
    <traceback @ 0x3323ef0>

    Lowercase name because that it's a class is an implementation detail.

    """

    def __init__(self, *exc_cls):
        self.exc_cls = exc_cls

    def __enter__(self):
        # For access to the exception later.
        return self

    def __exit__(self, typ, value, tb):
        assert typ, 'No exception raised.'
        assert typ in self.exc_cls, '%s not in %s' % (
            typ.__name__, [e.__name__ for e in self.exc_cls])
        self.exc_type = typ
        self.exception = value
        self.traceback = tb

        # Swallow expected exceptions.
        return True


@mock.patch.object(random, 'random', lambda: -1)
def test_incr():
    sc = _client()

    sc.incr('foo')
    _sock_check(sc, 1, 'foo:1|c')

    sc.incr('foo', 10)
    _sock_check(sc, 2, 'foo:10|c')

    sc.incr('foo', 1.2)
    _sock_check(sc, 3, 'foo:1.2|c')

    sc.incr('foo', 10, rate=0.5)
    _sock_check(sc, 4, 'foo:10|c|@0.5')


@mock.patch.object(random, 'random', lambda: -1)
def test_decr():
    sc = _client()

    sc.decr('foo')
    _sock_check(sc, 1, 'foo:-1|c')

    sc.decr('foo', 10)
    _sock_check(sc, 2, 'foo:-10|c')

    sc.decr('foo', 1.2)
    _sock_check(sc, 3, 'foo:-1.2|c')

    sc.decr('foo', 1, rate=0.5)
    _sock_check(sc, 4, 'foo:-1|c|@0.5')


@mock.patch.object(random, 'random', lambda: -1)
def test_gauge():
    sc = _client()
    sc.gauge('foo', 30)
    _sock_check(sc, 1, 'foo:30|g')

    sc.gauge('foo', 1.2)
    _sock_check(sc, 2, 'foo:1.2|g')

    sc.gauge('foo', 70, rate=0.5)
    _sock_check(sc, 3, 'foo:70|g|@0.5')


def test_gauge_delta():
    tests = (
        (12, '+12'),
        (-13, '-13'),
        (1.2, '+1.2'),
        (-1.3, '-1.3'),
    )

    def _check(num, result):
        sc = _client()
        sc.gauge('foo', num, delta=True)
        _sock_check(sc, 1, 'foo:%s|g' % result)

    for num, result in tests:
        yield _check, num, result


def test_gauge_absolute_negative():
    sc = _client()
    sc.gauge('foo', -5, delta=False)
    _sock_check(sc, 1, 'foo:0|g\nfoo:-5|g')


@mock.patch.object(random, 'random')
def test_gauge_absolute_negative_rate(mock_random):
    sc = _client()
    mock_random.return_value = -1
    sc.gauge('foo', -1, rate=0.5, delta=False)
    _sock_check(sc, 1, 'foo:0|g\nfoo:-1|g')

    mock_random.return_value = 2
    sc.gauge('foo', -2, rate=0.5, delta=False)
    _sock_check(sc, 1, 'foo:0|g\nfoo:-1|g')  # Should not have changed.


@mock.patch.object(random, 'random', lambda: -1)
def test_set():
    sc = _client()
    sc.set('foo', 10)
    _sock_check(sc, 1, 'foo:10|s')

    sc.set('foo', 2.3)
    _sock_check(sc, 2, 'foo:2.3|s')

    sc.set('foo', 'bar')
    _sock_check(sc, 3, 'foo:bar|s')

    sc.set('foo', 2.3, 0.5)
    _sock_check(sc, 4, 'foo:2.3|s|@0.5')


@mock.patch.object(random, 'random', lambda: -1)
def test_timing():
    sc = _client()

    sc.timing('foo', 100)
    _sock_check(sc, 1, 'foo:100|ms')

    sc.timing('foo', 350)
    _sock_check(sc, 2, 'foo:350|ms')

    sc.timing('foo', 100, rate=0.5)
    _sock_check(sc, 3, 'foo:100|ms|@0.5')


def test_prepare():
    sc = _client(None)

    tests = (
        ('foo:1|c', ('foo', '1|c', 1)),
        ('bar:50|ms|@0.5', ('bar', '50|ms', 0.5)),
        ('baz:23|g', ('baz', '23|g', 1)),
    )

    def _check(o, s, v, r):
        with mock.patch.object(random, 'random', lambda: -1):
            eq_(o, sc._prepare(s, v, r))

    for o, (s, v, r) in tests:
        yield _check, o, s, v, r


def test_prefix():
    sc = _client('foo')

    sc.incr('bar')
    _sock_check(sc, 1, 'foo.bar:1|c')


def _timer_check(cl, count, start, end):
    eq_(cl._sock.sendto.call_count, count)
    value = cl._sock.sendto.call_args[0][0].decode('ascii')
    exp = re.compile('^%s:\d+|%s$' % (start, end))
    assert exp.match(value)


def test_timer_manager():
    """StatsClient.timer is a context manager."""
    sc = _client()

    with sc.timer('foo'):
        pass

    _timer_check(sc, 1, 'foo', 'ms')


def test_timer_decorator():
    """StatsClient.timer is a thread-safe decorator."""
    sc = _client()

    @sc.timer('foo')
    def foo(a, b):
        return [a, b]

    @sc.timer('bar')
    def bar(a, b):
        return [b, a]

    # make sure it works with more than one decorator, called multiple times,
    # and that parameters are handled correctly
    eq_([4, 2], foo(4, 2))
    _timer_check(sc, 1, 'foo', 'ms')

    eq_([2, 4], bar(4, 2))
    _timer_check(sc, 2, 'bar', 'ms')

    eq_([6, 5], bar(5, 6))
    _timer_check(sc, 3, 'bar', 'ms')


def test_timer_capture():
    """You can capture the output of StatsClient.timer."""
    sc = _client()
    with sc.timer('woo') as result:
        eq_(result.ms, None)
    assert isinstance(result.ms, int)


@mock.patch.object(random, 'random', lambda: -1)
def test_timer_context_rate():
    sc = _client()

    with sc.timer('foo', rate=0.5):
        pass

    _timer_check(sc, 1, 'foo', 'ms|@0.5')


@mock.patch.object(random, 'random', lambda: -1)
def test_timer_decorator_rate():
    sc = _client()

    @sc.timer('foo', rate=0.1)
    def foo(a, b):
        return [b, a]

    @sc.timer('bar', rate=0.2)
    def bar(a, b=2, c=3):
        return [c, b, a]

    eq_([2, 4], foo(4, 2))
    _timer_check(sc, 1, 'foo', 'ms|@0.1')

    eq_([3, 2, 5], bar(5))
    _timer_check(sc, 2, 'bar', 'ms|@0.2')


def test_timer_context_exceptions():
    """Exceptions within a managed block should get logged and propagate."""
    sc = _client()

    with assert_raises(socket.timeout):
        with sc.timer('foo'):
            raise socket.timeout()

    _timer_check(sc, 1, 'foo', 'ms')


def test_timer_decorator_exceptions():
    """Exceptions from wrapped methods should get logged and propagate."""
    sc = _client()

    @sc.timer('foo')
    def foo():
        raise ValueError()

    with assert_raises(ValueError):
        foo()

    _timer_check(sc, 1, 'foo', 'ms')


def test_timer_object():
    sc = _client()

    t = sc.timer('foo').start()
    t.stop()

    _timer_check(sc, 1, 'foo', 'ms')


def test_timer_object_no_send():
    sc = _client()

    t = sc.timer('foo').start()
    t.stop(send=False)
    _sock_check(sc, 0)

    t.send()
    _timer_check(sc, 1, 'foo', 'ms')


@mock.patch.object(random, 'random', lambda: -1)
def test_timer_object_rate():
    sc = _client()

    t = sc.timer('foo', rate=0.5)
    t.start()
    t.stop()

    _timer_check(sc, 1, 'foo', 'ms@0.5')


def test_timer_object_no_send_twice():
    sc = _client()

    t = sc.timer('foo').start()
    t.stop()

    with assert_raises(RuntimeError):
        t.send()


def test_timer_send_without_stop():
    sc = _client()
    with sc.timer('foo') as t:
        assert t.ms is None
        with assert_raises(RuntimeError):
            t.send()

    t = sc.timer('bar').start()
    assert t.ms is None
    with assert_raises(RuntimeError):
        t.send()


def test_timer_object_stop_without_start():
    sc = _client()
    with assert_raises(RuntimeError):
        sc.timer('foo').stop()


def test_pipeline():
    sc = _client()
    pipe = sc.pipeline()
    pipe.incr('foo')
    pipe.decr('bar')
    pipe.timing('baz', 320)
    pipe.send()
    _sock_check(sc, 1, 'foo:1|c\nbar:-1|c\nbaz:320|ms')


def test_pipeline_null():
    """Ensure we don't error on an empty pipeline."""
    sc = _client()
    pipe = sc.pipeline()
    pipe.send()
    _sock_check(sc, 0)


def test_pipeline_manager():
    sc = _client()
    with sc.pipeline() as pipe:
        pipe.incr('foo')
        pipe.decr('bar')
        pipe.gauge('baz', 15)
    _sock_check(sc, 1, 'foo:1|c\nbar:-1|c\nbaz:15|g')


def test_pipeline_timer_manager():
    sc = _client()
    with sc.pipeline() as pipe:
        with pipe.timer('foo'):
            pass
    _timer_check(sc, 1, 'foo', 'ms')


def test_pipeline_timer_decorator():
    sc = _client()
    with sc.pipeline() as pipe:
        @pipe.timer('foo')
        def foo():
            pass
        foo()
    _timer_check(sc, 1, 'foo', 'ms')


def test_pipeline_timer_object():
    sc = _client()
    with sc.pipeline() as pipe:
        t = pipe.timer('foo').start()
        t.stop()
        _sock_check(sc, 0)
    _timer_check(sc, 1, 'foo', 'ms')


def test_pipeline_empty():
    """Pipelines should be empty after a send() call."""
    sc = _client()
    with sc.pipeline() as pipe:
        pipe.incr('foo')
        eq_(1, len(pipe._stats))
    eq_(0, len(pipe._stats))


def test_pipeline_packet_size():
    """Pipelines shouldn't send packets larger than 512 bytes."""
    sc = _client()
    pipe = sc.pipeline()
    for x in range(32):
        # 32 * 16 = 512, so this will need 2 packets.
        pipe.incr('sixteen_char_str')
    pipe.send()
    eq_(2, sc._sock.sendto.call_count)
    assert len(sc._sock.sendto.call_args_list[0][0][0]) <= 512
    assert len(sc._sock.sendto.call_args_list[1][0][0]) <= 512


def test_pipeline_negative_absolute_gauge():
    """Negative absolute gauges use an internal pipeline."""
    sc = _client()
    with sc.pipeline() as pipe:
        pipe.gauge('foo', -10, delta=False)
        pipe.incr('bar')
    _sock_check(sc, 1, 'foo:0|g\nfoo:-10|g\nbar:1|c')


def test_big_numbers():
    num = 1234568901234
    result = 'foo:1234568901234|%s'
    tests = (
        # Explicitly create strings so we avoid the bug we're trying to test.
        ('gauge', 'g'),
        ('incr', 'c'),
        ('timing', 'ms'),
    )

    def _check(method, suffix):
        sc = _client()
        getattr(sc, method)('foo', num)
        _sock_check(sc, 1, result % suffix)

    for method, suffix in tests:
        yield _check, method, suffix


@mock.patch.object(random, 'random', lambda: 2)
def test_rate_no_send():
    sc = _client()
    sc.incr('foo', rate=0.5)
    _sock_check(sc, 0)


def test_socket_error():
    sc = _client()
    sc._sock.sendto.side_effect = socket.timeout()
    sc.incr('foo')
    _sock_check(sc, 1, 'foo:1|c')
