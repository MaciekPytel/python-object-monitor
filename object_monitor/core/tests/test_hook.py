import unittest

from object_monitor.core import hook
from mock_monitor import MockMonitor


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
        self.assertFalse(hasattr(test_cls, '_monitor_counter'))
        instance = test_cls()
        self.assertFalse(hasattr(instance, '_monitor_id'))
        self.assertEquals(MockMonitor.get_states(test_cls), {})

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

    @unittest.skip('This is a known issue with monitor decorator')
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
        self.assertEquals(base_instance.param, 42)
        self.check_unmonitored(base)

        # make sure __init__ from baseclass gets executed and monitoring works
        instance = cls()
        self.assertEquals(instance.param, 42)
        instance_id = instance._monitor_id
        self.assertEqual(MockMonitor.get_state(cls, instance_id),
                         MockMonitor.STATE_INITIALISED)
        instance = None
        self.assertEqual(MockMonitor.get_state(cls, instance_id),
                         MockMonitor.STATE_DESTROYED)

    @unittest.skip('This is a known issue with monitor decorator')
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
