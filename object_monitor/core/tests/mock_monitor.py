import weakref

from object_monitor.core import monitor


class MockMonitor(monitor.Monitor):
    '''
    Custom monitor mock used in testing.

    Remembers the state of all instances (based on classname & instance id).
    '''
    STATE_INITIALISED = 'initialised'
    STATE_DESTROYED = 'destroyed'

    _monitors = {}

    def __init__(self, original_cls, monitored_cls):
        super(MockMonitor, self).__init__(original_cls, monitored_cls)
        self.cls_name = monitored_cls.__name__
        if self.cls_name in self._monitors:
            raise AssertionError('Class {} monitored more than once'.
                                 format(self.cls_name))
        self._monitors[self.cls_name] = self
        self._instances = {}

    def on_init(self, instance, instance_id):
        if instance.__class__.__name__ != self.cls_name:
            raise AssertionError('Instance of class {} passed to class {} '
                                 'monitor'.format(instance.__class__.__name__,
                                                  self.cls_name))
        if instance_id in self._instances:
            raise AssertionError('Multiple inits on instance {} of '
                                 'class {}'.format(instance_id, self.cls_name))
        self._instances[instance_id] = self.STATE_INITIALISED

    def on_destroy(self, instance_id):
        if instance_id not in self._instances:
            raise AssertionError('Trying to destroy uninitialised instance '
                                 'of class {}'.format(self.cls_name))
        if self._instances[instance_id] == self.STATE_DESTROYED:
            raise AssertionError('Instance {} of class {} destroyed twice'.
                                 format(instance_id, self.cls_name))
        self._instances[instance_id] = self.STATE_DESTROYED

    @classmethod
    def is_monitored(cls, monitored_cls):
        ''' Check if a given class is monitored. '''
        return monitored_cls.__name__ in cls._monitors

    @classmethod
    def get_states(cls, monitored_cls):
        ''' Get states of all instances of monitored class. '''
        monitor = cls._monitors.get(monitored_cls.__name__)
        return monitor._instances if monitor is not None else {}

    @classmethod
    def get_state(cls, monitored_cls, instance_id):
        ''' Get state of a given instance of monitored class. '''
        return cls.get_states(monitored_cls).get(instance_id)

    @classmethod
    def reset(cls):
        ''' Delete all existing monitoring information. '''
        cls._monitors.clear()
