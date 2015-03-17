class Monitor(object):
    ''' Base class for object monitors. '''
    def __init__(self, original_cls, monitored_cls):
        self._cls = monitored_cls

    def on_init(self, instance, instance_id):
        '''
        Callback called after an instance of monitored class is initialised.

        More precisely - this is called just after instance's __init__ method.

        Params:
        instance - newly created instance of monitored class
        instance_id - a unique id assigned to instance (this will be passed
            to any monitoring method related to this instance).
        '''
        pass

    def on_destroy(self, instance_id):
        '''
        Callback called after instance of a monitored class gets deallocated.

        At the time of this call the instance doesn't exist anymore. Any state
        necessary in this method must be referenced from outside the instance
        and be accessible based on instance_id. Be careful not to create cycles
        or memory leak when referencing state from outside!

        Params:
        instance_id - a unique id assigned to instance that was just
            deallocated.
        '''
        pass

    def is_monitoring(self, obj):
        '''
        Check if a given object is monitored by this monitor.

        This is used internally to check if monitor callbacks
        should be called.
        '''
        return obj.__class__ is self._cls
