import unittest

from object_monitor.core import hook
from mock_monitor import MockMonitor


class HookTest(unittest.TestCase):
    def tearDown(self):
        MockMonitor.reset()

    def check_monitored(self, test_cls):
        self.assertTrue(MockMonitor.is_monitored(test_cls))

        instance1 = test_cls()
        instance2 = test_cls()
        id1 = instance1._monitor_id
        id2 = instance2._monitor_id

        instance1 = None
        self.assertEqual(MockMonitor.get_state(test_cls, id1),
                         MockMonitor.STATE_DESTROYED)
        self.assertEqual(MockMonitor.get_state(test_cls, id2),
                         MockMonitor.STATE_INITIALISED)

    def test_hook_empty_class(self):
        cls = type('SampleClass', (object,), {})
        cls = hook.monitor(MockMonitor)(cls)
        self.check_monitored(cls)

    def test_hook_with_simple_baseclass(self):
        base = type('SampleBase', (object,), {})
        cls = type('SampleClass', (base,), {})
        cls = hook.monitor(MockMonitor)(cls)

        self.check_monitored(cls)

        # make sure we haven't decorated base class
        self.assertFalse(MockMonitor.is_monitored(base))
        self.assertFalse(hasattr(base, '_monitor_counter'))
        base_instance = base()
        self.assertFalse(hasattr(base_instance, '_monitor_id'))
        self.assertEquals(MockMonitor.get_states(base), {})


