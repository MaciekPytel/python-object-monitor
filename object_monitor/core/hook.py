import functools
import weakref


class MonitorReference(object):
    '''
    A simple proxy class for monitor.

    This is used when we need to access monitor in decorators and
    similar - the monitor itself doesn't exist yet, so we pass
    a reference, which we bind to actual monitor when it gets created.

    An object proxy would probably be a nicer solution, but doing one
    properly is quite complex in python, so we'll make do with this
    at least for now.
    '''
    def bind(self, monitor):
        self._monitor = weakref.ref(monitor)

    def __call__(self):
        if hasattr(self, '_monitor'):
            return self._monitor()
        return None


def monitor_decorator(decorator_fn):
    '''
    Use this to decorate your own decorators hooked on monitored object.

    This decorator checks if the instance on which the method is called should
    indeed be monitored. If so the decorated version of the method is called.
    Otherwise (for example if it's an instance of a class derived from
    monitored class) a base version of the method will be called instead.

    This already uses functools.wraps no need to use it in your decorator.
    '''
    def decorator(method, monitor_ref):
        decorated = decorator_fn(method)

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if monitor_ref().is_monitoring(self):
                return decorated(self, *args, **kwargs)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def _delegated_close(ref, cls, instance_id):
    cls._monitor.on_destroy(instance_id)
    cls._weakrefs.remove(ref)


@monitor_decorator
def _init_decorator(original_init):
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


def _decorate_method(clsdict, name, decorator, monitor_ref):
    # BEWARE: Here be dragons.
    #
    # What if a method is not defined by cls, but coming from one of its base
    # classes instead? What if that's the case AND you want to further derive
    # non-monitored classes from your monitored class?
    # We need a dummy method we can decorate without decorating the original
    # method in baseclass. But what if we were to call this wrapper from
    # a derived class? We need to make sure our wrapper method indeed calls
    # the method from the baseclass of monitored class.
    # It is very easy to create endless recursion here.

    def basemethod_wrapper(self, *args, **kwargs):
        method = getattr(super(self._monitor._cls, self), name)
        return method(*args, **kwargs)

    if name in clsdict:
        method = clsdict[name]
    else:
        method = basemethod_wrapper
    clsdict[name] = decorator(method, monitor_ref)


def monitor(monitor_cls):
    '''
    Class decorator - will start monitoring given class using a given monitor.

    Params:
    monitor_cls - a class implementing Monitor interface; this class will be
        instantiated per each monitored class (one Monitor instance per
        monitored class)

    NOTE: This decorator doesn't (yet) support nesting - if you want to apply
    multiple you need to combine their functionality into a single Monitor
    class.
    '''
    def wrap(cls):
        monitor_ref = MonitorReference()
        clsdict = dict(cls.__dict__)
        _decorate_method(clsdict, '__init__', _init_decorator, monitor_ref)
        clsdict['_monitor_counter'] = 0
        clsdict['_weakrefs'] = set()

        newcls = type(cls.__name__, cls.__bases__, clsdict)
        newcls._monitor = monitor_cls(cls, newcls)
        monitor_ref.bind(newcls._monitor)
        return newcls
    return wrap
