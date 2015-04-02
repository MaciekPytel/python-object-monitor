import functools
import time
import weakref

from object_monitor.core.hook import monitor_decorator


class Monitor(object):
    ''' Base class for object monitors. '''

    _monitors = []

    ''' A list of methods that will be captured by monitor. '''
    HOOK_METHODS = []

    def __init__(self, original_cls, monitored_cls):
        self._cls = monitored_cls
        self._monitors.append(self)

    def on_init(self, instance, instance_id, *args, **kwargs):
        '''
        Callback called after an instance of monitored class is initialised.

        More precisely - this is called just after instance's __init__ method.

        Params:
        instance - newly created instance of monitored class
        instance_id - a unique id assigned to instance (this will be passed
            to any monitoring method related to this instance)
        args - positional arguments passed to class __init__ method
        kwargs - keyword arguments passed to class __init__ method
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
                result, error, mtime, *args, **kwargs):
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
        mtime - time elapsed in method
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

    @staticmethod
    @monitor_decorator
    def _init_decorator(original_init):
        '''
        Decorator for init method of monitored class.

        You shouldn't normally need to modify this method.
        '''
        def _delegated_close(ref, cls, instance_id):
            cls._monitor.on_destroy(instance_id)
            cls._weakrefs.remove(ref)

        def wrapper(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self._monitor_id = self._monitor_counter
            self.__class__._monitor_counter += 1
            close_fn = functools.partial(_delegated_close,
                                         cls=self.__class__,
                                         instance_id=self._monitor_id)
            self._weakrefs.add(weakref.ref(self, close_fn))
            self._monitor.on_init(self, self._monitor_id)
        return wrapper

    @staticmethod
    @monitor_decorator
    def _method_decorator(method):
        '''
        Decorator for hooked methods.

        You may need to override this if you want to do a specific
        setup before method is executed.
        '''
        name = method.__name__

        def wrapper(self, *args, **kwargs):
            result = None
            error = None
            mtime = time.time()
            try:
                result = method(self, *args, **kwargs)
            except Exception as ex:
                error = ex
                raise ex
            finally:
                mtime = time.time() - mtime
                self._monitor.on_call(self, self._monitor_id, name,
                                      result, error, mtime, *args, **kwargs)
        return wrapper
