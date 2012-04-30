deconf
======

An object system for building declarative configurations in Python.

Deconfigurable is a class that has rich(ish) keyword-parameter handling including
explicit handling of required parameters and declaration of parameter
dependencies.

Keyword parameter processing will be performed for any method on the
Configurable that is decorated with the 'parameter' decorator. Each of these
decorated methods performs the processing specific to that parameter.

    >>> @parameter('foo')
    >>> def handle_foo(self, kwargs):
    ...    self.foo = kwargs.get('foo')
    ...    return self.foo

REQUIRED PARAMETERS:

Parameters are required by default. This means that a RequiredParameterError
will be raised if the Configurable.__init__ doesn't recieve the designated
named argument. 

Passing `required=False` to @parameter will prevent the parameter from
raising RequiredParameterError if the parameter isn't provided a value. If
the parameter does not return a default value then None will be used.

    >>> @parameter('foo', required=False)
    >>> def handle_foo(self, kwargs):
    ...    self.foo = kwargs.get('foo', 'bar')
    ...    return self.foo


DEPENDENCY PARAMETERS:
   
Sometimes we will want to defer processing of a parameter until some other
parameter has been processed first. To do so, simply pass a list of
dependencies, `depends_on`, to @parameter.

    >>> @parameter('bar', depends_on=('foo', ))
    >>> def handle_bar(self, kwargs):
    ...     self.bar = kwargs.get('bar')
    ...     return self.bar