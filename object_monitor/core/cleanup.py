import atexit
import os
import signal

from object_monitor.core import monitor


SIGNALS = [signal.SIGTERM, signal.SIGINT]
_handlers = {}


def _run_cleanup():
    for mon in monitor.Monitor._monitors:
        mon.atexit()


def _signal_handler(sig, frame):
    handler = _handlers.get(sig)
    if handler == signal.SIG_IGN:
        return
    _run_cleanup()
    if handler is None or handler == signal.SIG_DFL:
        signal.signal(sig, signal.SIG_DFL)
    else:
        signal.signal(sig, handler)
    os.kill(os.getpid(), sig)


def _register_signals():
    for sig in SIGNALS:
        handler = signal.getsignal(sig)
        if sig is None or sig == signal.SIG_IGN:
            continue
        _handlers[sig] = handler
        signal.signal(sig, _signal_handler)


def register_cleanup():
    atexit.register(_run_cleanup)
    _register_signals()
