import os, imp

class RequiredParameterError(Exception): pass
class CyclicalDependencyError(Exception): pass
class ParameterTypeError(Exception): pass
class ParameterValueError(Exception): pass

def load_config(filename):
    basename = os.path.basename(filename)
    parts = basename.split('.')
    modname = parts[0]
    path = os.path.abspath(filename)
    if os.path.exists(path):
        return imp.load_source(modname, path)

class Deconfigurable(object):
    '''
    A class that has rich(ish) keyword-parameter handling including explicit
    handling of required parameters and declaration of parameter dependencies.

    Keyword parameter processing will be performed for any method on the
    Deconfigurable that is decorated with the `@parameter` decorator. Each of these
    decorated methods performs the processing specific to that parameter. The 
    returned value is then assigned on the appropriately named attribute.

    >>> @parameter('foo')
    >>> def handle_foo(self, value):
    ...    return value


    PASS-THROUGH PARAMETERS:

    If your parameter doesn't require any special treatment and should simply
    be stored on the `Deconfigurable` a shorthand can be used. Simply decorate 
    a parameter method that passes, and `value` will be used as is.

    >>> @parameter('foo')
    >>> def handle_foo(self, value):
    ...    pass


    REQUIRED PARAMETERS:

    Parameters are required by default. This means that a RequiredParameterError
    will be raised if the Deconfigurable.__init__ doesn't recieve the designated
    named argument. 

    Passing `default=` to @parameter will prevent the parameter from
    raising RequiredParameterError if the parameter isn't provided a value.

    >>> @parameter('foo', default='bar')
    >>> def handle_foo(self, value):
    ...    pass


    TYPE-CHECKED PARAMETERS:

    A basic mechanism is supplied for ensuring that the passed parameter value
    is of a specific type. By supplying a type value to the @parameter's
    `ensure_type` keyword arguement any value passed in will be validated with
    an isinstance check.

    >>> @parameter('bars', ensure_type=list)
    >>> def handle_bars(self, value):
    ...     pass


    DEPENDENCY PARAMETERS:
   
    Sometimes we will want to defer processing of a parameter until some other
    parameter has been processed first. To do so, simply pass a list of
    dependencies, `depends_on`, to @parameter.

    >>> @parameter('foo')
    >>> def handle_foo(self, foo):
    ...    pass

    >>> @parameter('bar', depends_on=('foo', ))
    >>> def handle_bar(self, bar):
    ...     # offset bar by foo
    ...     return bar + self.foo 



    EXAMPLE:

    class Person(Deconfigurable):
        @staticmethod
        def format_name(cls, name):
            return name.strip().lower().capitalize()

        @parameter('first_name', ensure_type=str)
        def handle_first(self, name): 
            return Person.format_name(name)

        @parameter('last_name', ensure_type=str)
        def handle_last(self, name):
            return Person.format_name(name)

        @parameter('age', ensure_type=int)
        def handle_age(self, value): pass

        @parameter('registered_to_vote', ensure_type=bool, depends_on=('age',))
        def handle_vote(self, value):
            if self.age < 18:
                value = False
            return value

    >>> me = Person(
    ...    first_name='Dustin',
    ...    last_name='Lacewell',
    ...    age=25, registered_to_vote=True,
    ... )
    >>> print me.first_name, ' can vote: ', me.registered_to_vote
    Dustin can vote: True

    >>> kid = Person(
    ...    first_name='Some Kid',
    ...    last_name='Smith',
    ...    age=12, registered_to_vote=True,
    ... )
    >>> print kid.first_name, ' can vote: ', kid.registered_to_vote
    SomeKid can vote: False
    '''

    def __init__(self, **kwargs):
        self._param_methods = self._get_param_methods()
        self._param_vals = {}
        for param, method in self._param_methods.items():
            self._process_param(param, method, kwargs)
        
    def _get_param_methods(self):
        methods = {}
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and hasattr(attr, '__param__'):
                methods[attr.__param__] = attr
        return methods

    def _process_param(self, param, method, kwargs, chain=None):
        if chain == None:
            chain = []
        chain.append(param)
        # process dependencies
        deps = getattr(method, '__dependencies__', [])
        for depname in deps:
            # cyclical dependency
            if depname in chain:
                msg = "Cyclical dependency discovered while processing '%s'."
                ctx = (chain[0], )
                raise CyclicalDependencyError(msg % ctx)
            dep_method = self._param_methods.get(depname, None)
            # new dependency
            if depname not in self._param_vals:
                self._process_param(depname, dep_method, kwargs, chain=chain)
            # failed dependency
            if depname not in self._param_vals:
                msg = "'%s' object missing required '%s' parameter."
                ctx = (self.__class__.__name__, depname)
                raise RequiredParameterError(msg % ctx)                

        self._param_vals[param] = method(kwargs)

class Undefined(object): pass

def parameter(param, depends_on=tuple(), ensure_type=None, default=Undefined):
    def decorator(f):
        def wrapper(self, kwargs):
            if param in kwargs:
                val = kwargs[param]
                if ensure_type and not isinstance(val, ensure_type):
                    msg = "'{0}' parameter must be a '{1}' instance."
                    raise ParameterTypeError(msg.format(param, ensure_type))
            else:
                if default != Undefined:
                    val = default
                else:
                    msg = "'%s' object missing required '%s' parameter."
                    ctx = (self.__class__.__name__, param)
                    raise RequiredParameterError(msg % ctx)
            retval = f(self, val)
            setattr(self, param, retval or val)
        wrapper.__param__ = param
        wrapper.__dependencies__ = depends_on
        return wrapper
    return decorator
