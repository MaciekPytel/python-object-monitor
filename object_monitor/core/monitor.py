class Monitor(object):
    ''' Base class for object monitors. '''

    _monitors = []

    ''' A list of methods that will be captured by monitor. '''
    HOOK_METHODS = []

    def __init__(self, original_cls, monitored_cls):
        self._cls = monitored_cls
        self._monitors.append(self)

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

    def on_call(self, instance, instance_id, method_name,
                result, error, *args, **kwargs):
        '''
        Callback called when a method is called on instance.

        This is called right after a method finished executing (even if
        it raised an exception). It will only be called for registered
        methods.

        Params:
        instance - instance on which the method was called
        instance_id - a unique id of instance
        method_name - string with a name of the called method
        result - value returned by method
        error - any exception raised by the method (or None if no
            exception was raised)
        args - positional parameters passed to method (not including
            self)
        kwargs - keyword parameters passed to method
        '''
        pass

    def is_monitoring(self, obj):
        '''
        Check if a given object is monitored by this monitor.

        This is used internally to check if monitor callbacks
        should be called.
        '''
        return obj.__class__ is self._cls

    def atexit(self):
        '''
        Callback that will be called at program end.

        This is meant to provide a hook to analyse and store any data
        collected by monitor.
        NOTE: currently it will only be called if a program exits
        normally (not by signal or exit()).
        '''
        pass
