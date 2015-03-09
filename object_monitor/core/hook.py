import functools
import weakref


def _delegated_close(ref, cls, instance_id):
    cls._monitor.on_destroy(instance_id)
    cls._weakrefs.remove(ref)


def _init_decorator(original_init):
    @functools.wraps(original_init)
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


def _decorate_method(clsdict, name, decorator):
    '''
    Override a method with a decorated one.

    There is some trickiness here - what if a method is not defined by cls,
    but coming from one of its base classes instead?
    To get a reasonable behavior in this case we're creating a dummy method
    that just calls itself on base using super and decorate that dummy method.
    '''
    def basemethod_wrapper(self, *args, **kwargs):
        method = getattr(super(self.__class__, self), name)
        return method(*args, **kwargs)

    if name in clsdict:
        method = clsdict[name]
    else:
        method = basemethod_wrapper
    clsdict[name] = decorator(method)


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
    NOTE: As this modifies the class any derived class not overriding __init__
    will also be monitored. This will hopefully be fixed soon.
    '''
    # TODO(Maciek): fix the stuff mentioned in above docstring
    def wrap(cls):
        clsdict = dict(cls.__dict__)
        _decorate_method(clsdict, '__init__', _init_decorator)
        clsdict['_monitor_counter'] = 0
        clsdict['_weakrefs'] = set()

        newcls = type(cls.__name__, cls.__bases__, clsdict)
        newcls._monitor = monitor_cls(cls, newcls)
        return newcls
    return wrap
