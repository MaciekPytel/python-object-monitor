import unittest

from mock_monitor import MockMonitor
from object_monitor.core import hook


def dummy_init(self):
    ''' A dummy function used as __init__ in test classes. '''
    self.param = 42


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

    def check_unmonitored(self, test_cls):
        self.assertFalse(MockMonitor.is_monitored(test_cls))
        instance = test_cls()
        self.assertFalse(hasattr(instance, '_monitor_id'))
        self.assertEqual(MockMonitor.get_states(test_cls), {})

    def test_hook_empty_class(self):
        cls = type('SampleClass', (object,), {})
        cls = hook.monitor(MockMonitor)(cls)
        self.check_monitored(cls)

    def test_hook_simple_baseclass(self):
        base = type('SampleBase', (object,), {})
        cls = type('SampleClass', (base,), {})
        cls = hook.monitor(MockMonitor)(cls)
        self.check_monitored(cls)
        self.check_unmonitored(base)

    def test_hook_simple_derived(self):
        cls = type('SampleClass', (object,), {})
        cls = hook.monitor(MockMonitor)(cls)
        derived = type('SampleDerived', (cls,), {})
        self.check_monitored(cls)
        self.check_unmonitored(derived)

    def test_hook_init_in_baseclass(self):
        base = type('SampleBase', (object,), {'__init__': dummy_init})
        cls = type('SampleClass', (base,), {})
        cls = hook.monitor(MockMonitor)(cls)

        # make sure we didn't break __init__ in baseclass
        base_instance = base()
        self.assertEqual(base_instance.param, 42)
        self.check_unmonitored(base)

        # make sure __init__ from baseclass gets executed and monitoring works
        instance = cls()
        self.assertEqual(instance.param, 42)
        instance_id = instance._monitor_id
        self.assertEqual(MockMonitor.get_state(cls, instance_id),
                         MockMonitor.STATE_INITIALISED)
        instance = None
        self.assertEqual(MockMonitor.get_state(cls, instance_id),
                         MockMonitor.STATE_DESTROYED)

    def test_hook_init_usedby_derived(self):
        cls = type('SampleClass', (object,), {'__init__': dummy_init})
        cls = hook.monitor(MockMonitor)(cls)
        derived = type('SampleDerived', (cls,), {})
        self.check_monitored(cls)

        # make sure derived class is not monitored,
        # but was properly initialised
        self.check_unmonitored(derived)
        derived_instance = derived()
        self.assertEqual(derived_instance.param, 42)

    def test_base_and_derived_monitored(self):
        cls = type('SampleClass', (object,), {'__init__': dummy_init})
        cls = hook.monitor(MockMonitor)(cls)
        derived = type('SampleDerived', (cls,), {})
        derived = hook.monitor(MockMonitor)(derived)

        base_instance = cls()
        self.assertEqual(base_instance.param, 42)
        self.assertEqual(len(MockMonitor.get_states(cls)), 1)
        self.assertEqual(len(MockMonitor.get_states(derived)), 0)

        derived1 = derived()
        derived2 = derived()
        self.assertEqual(derived1.param, 42)
        self.assertEqual(len(MockMonitor.get_states(cls)), 1)
        self.assertEqual(len(MockMonitor.get_states(derived)), 2)
