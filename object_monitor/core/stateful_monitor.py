from object_monitor.core import Monitor


class StatefulMonitor(Monitor):
    '''
    Base class for monitors keeping monitored objects metadata.

    Most non-trivial monitors will likely be derived from this class.
    '''
    def __init__(self, original_cls, monitored_cls):
        super(StatefulMonitor, self).__init__(original_cls, monitored_cls)
        self._instances = {}

    def register_instance(self, instance, instance_id):
        '''
        Callback for initialising object metadata.

        This will be called when an object is created and the returned value
        will be stored by monitor. It can be later accessed and modified
        by using get_instance_data() and set_instance_data().
        '''
        raise NonImplemented()

    def on_init(self, instance, instance_id):
        self._instances[instance_id] = self.register_instance(instance,
                                                              instance_id)

    def get_instance_data(self, instance=None, instance_id=None):
        '''
        Get instance metadata.

        Either instance or instance or instance_id can be used to retrieve
        metadata. Also works if both are provided unless they point to a
        different object (in which case ValueError will be raised).

        Returns None if no data is available for object.
        '''
        if instance_id is None:
            instance_id = instance._monitor_id
        if instance is not None and instance._monitor_id != instance_id:
            raise ValueError('Trying to retrieve two different objects in a '
                             'single get_instance_data call')
        return self._instances.get(instance_id)

    def set_instance_data(self, instance=None, instance_id=None, data=None):
        '''
        Set instance metadata.

        Either instance or instance or instance_id can be used to retrieve
        metadata. Also works if both are provided unless they point to a
        different object (in which case ValueError will be raised).
        '''
        if instance_id is None:
            instance_id = instance._monitor_id
        if instance is not None and instance._monitor_id != instance_id:
            raise ValueError('Trying to set metadata of two different objects '
                             'in a single set_instance_data call')
        self._instances[instance_id] = data
