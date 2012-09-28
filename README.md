deconf
======

An object system for building declarative configurations in Python.

A class that has rich(ish) keyword-parameter handling, including 
[explicit handling of required parameters](https://github.com/dustinlacewell/deconf#pass-through-parameters),
[declaration of parameter dependencies](https://github.com/dustinlacewell/deconf#dependency-parameters) and
[basic type-checking](https://github.com/dustinlacewell/deconf#type-checked-parameters).

Keyword parameter processing will be performed for any method on the
`Deconfigurable` that is decorated with the `@parameter` decorator. Each of these
decorated methods performs the processing specific to that parameter. The 
returned value is then assigned on the appropriately named attribute.


    >>> @parameter('foo')
    >>> def handle_foo(self, value):
    ...    return value


Pass-Through Parameters:
------------------------

If your parameter doesn't require any special treatment and should simply
be stored on the Deconfigurable a shorthand can be used. Simply decorate 
a parameter method that passes, and `value` will be used as is.


    >>> @parameter('foo')
    >>> def handle_foo(self, value):
    ...    pass


Required Parameters:
--------------------

Parameters are required by default. This means that a `RequiredParameterError`
will be raised if the `Deconfigurable.__init__` doesn't recieve the designated
named argument. 

Passing `default=` to `@parameter` will prevent the parameter from
raising `RequiredParameterError` if the parameter isn't provided a value.


    >>> @parameter('foo', default='bar')
    >>> def handle_foo(self, value):
    ...    pass


Type-Checked Parameters:
------------------------

A basic mechanism is supplied for ensuring that the passed parameter value
is of a specific type. By supplying a type value to the `@parameter`'s
`ensure_type` keyword arguement any value passed in will be validated with
an *isinstance check*.


    >>> @parameter('bars', ensure_type=list)
    >>> def handle_bars(self, value):
    ...     pass


Dependency Parameters:
----------------------
   
Sometimes we will want to defer processing of a parameter until some other
parameter has been processed first. To do so, simply pass a list of
dependencies, `depends_on`, to `@parameter`.


    >>> @parameter('foo')
    >>> def handle_foo(self, foo):
    ...    pass

    >>> @parameter('bar', depends_on=('foo', ))
    >>> def handle_bar(self, bar):
    ...     # offset bar by foo
    ...     return bar + self.foo 


Contrived Example:
------------------

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



Example from Spidersilk (twisted.web config lib):
-------

    from twisted.web.static import File
    from twisted.web.proxy import ReverseProxyResource

    from spidersilk import Domain, Httpd

    application = Httpd(
        port = 80,
        default = 'ldlework.com',
        domains = [
            Domain(
                hostname='ldlework.com',
                resource=File('/var/txweb/ldlework.com'),
            ),
            Domain(
                hostname='lichen.ldlework.com',
                resource=ReverseProxyResource('localhost', 8088, ''),
            ),
        ],
    )


Where Domain is implemented as:

    class Domain(Deconfigurable):
        @parameter('hostname', ensure_type=str)
        def _arg_hostname(self, hostname):
            pass

        @parameter('resource', ensure_type=twisted.web.resource.Resource)
        def _arg_resource(self, resource):
            pass


