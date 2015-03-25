import atexit
import signal

from object_monitor.core import monitor


def _run_cleanup():
    for mon in monitor.Monitor._monitors:
        mon.atexit()


atexit.register(_run_cleanup)
