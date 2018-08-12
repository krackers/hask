from __future__ import division, print_function, absolute_import

'''Internal Type System for Hask.

Defining `instances of typeclasses <hask.lang.syntax.instance>`:class: will
store a internal mapping on every `~hask.lang.typeclasses.Typeclass`:class:
(`__instances__` ) using a unique key for every new type generated by
`Typeclass.get_id`:meth: static method.  The corresponding values are special
`named-tuples <namedtuple>`:class: containing the member functions being added
(see `build_instance`:func: function.)

In the next example, the `Eq` typeclass is added to the type `Person` by
implementing the member function `eq`::

   class Person(object):
       def __init__(self, name, age):
           self.name = name
           self.age = age

   instance(Eq, Person).where(
       eq = lambda p1, p2: p1.name == p2.name and p1.age == p2.age
   )

'''

from xoutil.eight.meta import metaclass


class TypeMeta(type):
    """Metaclass for Typeclass type.

    Ensures that all typeclasses are instantiated with a dictionary to map
    instances to their member functions, and a list of dependencies.

    """

    def __init__(self, *args):
        super(TypeMeta, self).__init__(*args)
        self.__instances__ = {}
        # excl self, Typeclass, object
        self.__dependencies__ = self.mro()[1:-2]

    def __getitem__(self, item):
        from hask.lang.hindley_milner import ListType
        try:
            if isinstance(item, ADT):
                key = item.__type_constructor__
            elif isinstance(typeof(item), ListType):
                key = type(item)
            elif isinstance(item, Hask):
                key = typeof(item)
            else:
                key = type(item)
            return self.__instances__[self.get_id(key)]
        except KeyError:
            raise TypeError("No instance for {}".format(item))


class Typeclass(metaclass(TypeMeta)):
    """Base class for Hask type-classes.

    All subclasses should implement `make_instance` method, which controls
    what happens when a new instance is added.  It should set up whatever
    attributes/functions belong to the type-class, and then call
    `build_instance`:func:.  See `~hask.lang.typeclasses`:mod: module for
    examples.

    """
    __next_id__ = 1
    __readonly_types__ = {}

    @classmethod
    def make_instance(typeclass, type_, *args):
        raise NotImplementedError("Typeclasses must implement make_instance")

    @classmethod
    def derive_instance(typeclass, type_):
        raise NotImplementedError("Typeclasses must implement derive_instance")

    @staticmethod
    def get_id(key):
        '''Get the unique ID to obtain 'instance' member functions.'''
        UNSET = 'unset'
        magic = '__unique_typeclass_id__'
        res = getattr(key, magic, UNSET)
        if res is UNSET:
            cls = Typeclass
            res = cls.__readonly_types__.get(key, UNSET)
            if res is UNSET:
                # XXX: Note that this approach is *not* thread-safe
                res, cls.__next_id__ = cls.__next_id__, cls.__next_id__ + 1
                try:
                    setattr(key, magic, res)
                except TypeError:
                    try:
                        cls.__readonly_types__[key] = res
                    except TypeError:    # unhashable key
                        # likely never happening
                        try:
                            head = key.__name__
                        except AttributeError:
                            head = type(key).__name__
                        tail = str(id(key) % 1048576)
                        res = '.'.join((head, tail))
        return res


def build_instance(typeclass, cls, attrs):
    """Add a new instance to a `typeclass`.

    i.e. modify the type-class's instance dictionary to include the new
    instance.

    :param typeclass: The typeclass for which we are adding an instance.

    :param cls: The class or type to be added.

    :param attrs: A dict of ``{str: function}``, mapping function names to
           functions for the `typeclass` instance.

    :raises TypeError: if `cls` is not a member of all `typeclass`
            super-classes.

    """
    from collections import namedtuple
    deps = typeclass.__dependencies__
    key = Typeclass.get_id(cls)
    bad = next((dep for dep in deps if key not in dep.__instances__), None)
    if bad is None:
        name = '__{}_{}__'.format(typeclass.__name__, cls.__name__)
        typeclass.__instances__[key] = namedtuple(name, attrs.keys())(**attrs)
    else:
        raise TypeError("Missing dependency: '{}'".format(bad.__name__))


def has_instance(cls, typeclass):
    """Test whether a class is a member of a particular type-class.

    :param cls: The class or type to test for membership.

    :param typeclass: The typeclass to check.  Must be a subclass of
           `Typeclass`:class:.

    :returns: True if cls is a member of typeclass, and False otherwise.

    """
    ok = issubclass(typeclass, Typeclass)
    return ok and Typeclass.get_id(cls) in typeclass.__instances__


class Hask(object):
    """Base class for objects within hask.

    `ADTs <ADT>`:class:, `TypedFunc`:class:,
    `~hask.lang.lazylist.List`:class:, `Undefined`:class:, and other
    hask-related types are all subclasses of Hask.

    All sub-classes must redefine `__type__`, which returns a representation
    of the object in the internal type system language.

    """
    def __type__(self):
        raise TypeError()


class Undefined(Hask):
    """A class with no concrete type definition.

    So its type can unify with any other type.  Used to create `undefined`
    and to enable psuedo-laziness in pattern matching.

    """
    def __type__(self):
        from hask.lang.hindley_milner import TypeVariable
        return TypeVariable()


class PyFunc(object):
    """Singleton that represents (any of the) Python function types.

    This is in the type system and in type signatures.

    """


def typeof(obj):
    """Returns the type of an object within the internal type system.

    :param obj: the object to inspect.

    :returns: An object representing the type in the internal type system
              language (i.e., a
              `~hask.lang.hindley_milner.TypeOperator`:class:, or a
              `~hask.lang.hindley_milner.TypeVariable`:class:).

    """
    from hask.hack import is_python_function
    from hask.lang.hindley_milner import TypeVariable, TypeOperator, Tuple
    # XXX: WTF?
    TypeVariable.next_var_name = 'a'
    if isinstance(obj, Hask):
        return obj.__type__()
    elif isinstance(obj, tuple):
        return Tuple([typeof(o) for o in obj])
    elif obj is None:
        return TypeOperator(None, [])
    elif is_python_function(obj):
        return TypeOperator(PyFunc, [])
    else:
        return TypeOperator(type(obj), [])


# TODO: Implement string representation.
class TypeSignature(object):
    """Internal representation of a type signature.

    Consisting of a list of function type arguments and a list of (typeclass,
    type_variable) typeclass constraint pairs.

    """
    def __init__(self, args, constraints):
        self.args = args
        self.constraints = constraints


class TypeSignatureHKT(object):
    """Internal representation of a higher-kinded type within a signature.

    Consisting of the type constructor and its type parameter names.

    """
    def __init__(self, tcon, params):
        self.tcon = tcon
        self.params = params


class TypeSignatureError(Exception):
    pass


def build_sig_arg(arg, cons, var_dict):
    """Covert a type signature argument into its internal representation.

    :param arg: The argument (a string, a Python type, etc) to convert.

    :param cons: A dictionary of typeclass constraints for the type
           signature.

     :param var_dict: a dictionary of bound type variables.

    :returns: A TypeVariable or TypeOperator representing the `arg`.

    :raises TypeSignatureError: if the argument cannot be converted.

    """
    from hask.lang.hindley_milner import TypeVariable, TypeOperator
    from hask.lang.hindley_milner import Tuple, ListType
    if isinstance(arg, str):
        if arg.islower():
            if arg not in var_dict:
                kw = {'constraints': cons[arg]} if arg in cons else {}
                var_dict[arg] = TypeVariable(**kw)
            res = var_dict[arg]
        else:
            res = None
    # sub-signature, e.g. H/ (H/ int >> int) >> int >> int
    elif isinstance(arg, TypeSignature):
        res = make_fn_type(build_sig(arg, var_dict))
    # HKT, e.g. t(Maybe "a") or t("m", "a", "b")
    elif isinstance(arg, TypeSignatureHKT):
        if type(arg.tcon) == str:
            hkt = build_sig_arg(arg.tcon, cons, var_dict)
        else:
            hkt = arg.tcon
        types = [build_sig_arg(a, cons, var_dict) for a in arg.params]
        res = TypeOperator(hkt, types)
    # None (the unit type)
    elif arg is None:
        res = TypeOperator(None, [])
    # Tuples: ("a", "b"), (int, ("a", float)), etc.
    elif isinstance(arg, tuple):
        f = lambda x: build_sig_arg(x, cons, var_dict)
        res = Tuple([f(x) for x in arg])
    # Lists: ["a"], [int], etc.
    elif isinstance(arg, list):
        if len(arg) == 1:
            res = ListType(build_sig_arg(arg[0], cons, var_dict))
        else:
            res = None
    # any other type, builtin or user-defined
    elif isinstance(arg, type):
        res = TypeOperator(arg, [])
    else:
        res = None
    if res is not None:
        return res
    else:
        msg = "Invalid item in type signature: {}".format(arg)
        raise TypeSignatureError(msg)


def make_fn_type(params):
    """Turn type parameters into corresponding internal type system object.

    Returned object will represent the type of a function over the
    parameters.

    :param params: a list of type paramaters, e.g. from a type
           signature. These should be instances of TypeOperator or
           TypeVariable.

    :returns: An instance of TypeOperator representing the function type.

    """
    from hask.lang.hindley_milner import Function
    if len(params) == 2:
        last_input, return_type = params
        return Function(last_input, return_type)
    else:
        return Function(params[0], make_fn_type(params[1:]))


def build_sig(type_signature, var_dict=None):
    """Parse a TypeSignature to obtain the internal type system language.

    :param type_signature: an instance of TypeSignature.

    :param var_dict: a dictionary of already-bound type variables, or None.

    :returns: A list of TypeVariable/TypeOperator objects, representing the
              function type corresponding to the type signature.

    """
    args = type_signature.args
    cons = type_signature.constraints
    var_dict = {} if var_dict is None else var_dict
    return [build_sig_arg(i, cons, var_dict) for i in args]


# TODO: Implement string representation.
class TypedFunc(Hask):
    """Partially applied, statically typed function wrapper."""
    def __init__(self, fn, fn_args, fn_type):
        self.__doc__ = fn.__doc__
        self.func = fn
        self.fn_args = fn_args
        self.fn_type = fn_type

    def __type__(self):
        return self.fn_type

    def __call__(self, *args, **kwargs):
        # the environment contains the type of the function and the types
        # of the arguments
        from functools import partial
        from hask.lang.hindley_milner import Var, App
        from hask.lang.hindley_milner import unify
        # Using 'id' is an issue could produce errors.
        env = {id(self): self.fn_type}
        env.update({id(arg): typeof(arg) for arg in args})
        ap = Var(id(self))
        for arg in args:
            if isinstance(arg, Undefined):
                return arg
            ap = App(ap, Var(id(arg)))
        result_type = ap.analyze(env)

        if len(self.fn_args) - 1 == len(args):
            result = self.func(*args)
            unify(result_type, typeof(result))
            return result
        else:
            return type(self)(partial(self.func, *args, **kwargs),
                              self.fn_args[len(args):], result_type)

    def __mod__(self, arg):
        """(%) :: (a -> b) -> a -> b

        % is the apply operator, equivalent to $ in Haskell

        """
        return self.__call__(arg)

    def __mul__(self, fn):
        """(*) :: (b -> c) -> (a -> b) -> (a -> c)

        * is the function compose operator, equivalent to . in Haskell

        """
        from hask.lang.hindley_milner import Var, App, Lam
        if not isinstance(fn, TypedFunc):
            return fn.__rmul__(self)
        else:
            env = {id(self): self.fn_type, id(fn): fn.fn_type}
            app = App(Var(id(self)), App(Var(id(fn)), Var("arg")))
            compose = Lam("arg", app)
            newtype = compose.analyze(env)
            composed_fn = lambda x: self.func(fn.func(x))
            newargs = [fn.fn_args[0]] + self.fn_args[1:]
            return TypedFunc(composed_fn, fn_args=newargs, fn_type=newtype)


class ADT(Hask):
    """Base class for Hask Algebraic Data Types."""
    pass


def make_type_const(name, typeargs):
    """Build a new type constructor given a name and the type parameters.

    :param name: the name of the new type constructor to be created.

    :param typeargs: the type parameters to the constructor.

    :returns: A new class that acts as a type constructor.

    """
    from hask.lang.hindley_milner import TypeVariable, TypeOperator

    def raise_fn(err):
        raise err

    default_attrs = {"__params__": tuple(typeargs), "__constructors__": ()}
    cls = type(name, (ADT,), default_attrs)

    cls.__type__ = lambda self: \
        TypeOperator(cls, [TypeVariable() for i in cls.__params__])

    # Unless typeclass instances are provided or derived, ADTs do not support
    # any of these attributes, and trying to use one is a TypeError
    magic = {'iter', 'contains', 'add', 'radd', 'rmul', 'mul', 'lt', 'gt',
             'le', 'ge', 'eq', 'ne'}
    magic = {'__{}__'.format(op) for op in magic} | {'count', 'index'}
    for attr in magic:
        setattr(cls, attr, lambda self: raise_fn(TypeError))

    # Unless Show is instantiated/derived, use object's `repr` method
    cls.__repr__ = object.__repr__
    cls.__str__ = object.__str__

    return cls


def make_data_const(name, fields, type_constructor, slot_num):
    """Build a data constructor.

    The general approach is to create a subclass of the type constructor and a
    new class created with `namedtuple`, with some of the features from
    `namedtuple` such as equality and comparison operators stripped out.

    :param name: the name of the data constructor (a string).

    :param fields: the list of fields that the data constructor will have (a
           list of strings and types).

    :param type_constructor: constructor for the data constructor's type.

    :param slot_num: the position of the data constructor in the `data`
           statement defining the new type (e.g., Nothing=0, Just=1).

    :returns: The new data constructor.

    """
    from collections import namedtuple
    from hask.lang.hindley_milner import TypeVariable, TypeOperator
    # create the data constructor
    field_count = len(fields)
    base = namedtuple(name, ["i{}".format(i) for i in range(field_count)])
    cls = type(name, (type_constructor, base), {})
    cls.__type_constructor__ = type_constructor
    cls.__ADT_slot__ = slot_num

    if field_count == 0:
        # If the data constructor takes no arguments, create an instance of it
        # and return that instance rather than returning the class
        cls = cls()
    else:
        # Otherwise, modify __type__ so that it matches up fields from the data
        # constructor with type params from the type constructor
        def __type__(self):
            args = [
                typeof(self[fields.index(p)]) if p in fields else TypeVariable()
                for p in type_constructor.__params__
            ]
            return TypeOperator(type_constructor, args)
        cls.__type__ = __type__

    type_constructor.__constructors__ += (cls,)
    return cls


def build_ADT(typename, typeargs, data_constructors, to_derive):
    """Create a new Algebraic Data Type.

    A type constructor and at least one data constructor.

    :param typename: a string representing the name of the type constructor.

    :param typeargs: strings representing the type parameters of the type
           constructor (should be unique, lowercase strings).

    :param data_constructors: a list of (name, [field]) pairs representing
           each of the data constructors for the new type.

    :param to_derive: a list of typeclasses (subclasses of Typeclass) that
           should be derived for the new type.

    :returns: the type constructor, followed by each of the data constructors
              (in the order they were defined)

    Example usage::

        build_ADT(typename="Maybe",
                  typeargs=["a"],
                  data_constructors=[("Nothing", []), ("Just", ["a"])],
                  to_derive=[Read, Show, Eq, Ord])

    """
    # 1) Create the new type constructor and data constructors
    newtype = make_type_const(typename, typeargs)
    dcons = [make_data_const(dc_name, dc_fields, newtype, i)
             for i, (dc_name, dc_fields) in enumerate(data_constructors)]

    # 2) Derive typeclass instances for the new type constructor
    for tclass in to_derive:
        tclass.derive_instance(newtype)

    # 3) Wrap data constructors in TypedFunc instances
    for i, (dc_name, dc_fields) in enumerate(data_constructors):
        if len(dc_fields) != 0:
            return_type = TypeSignatureHKT(newtype, typeargs)
            sig = TypeSignature(list(dc_fields) + [return_type], [])
            sig_args = build_sig(sig, {})
            dcons[i] = TypedFunc(dcons[i], sig_args, make_fn_type(sig_args))
    return tuple([newtype] + dcons)


class PatternMatchBind(object):
    """Represents a local variable bound by pattern matching."""
    def __init__(self, name):
        self.name = name


class PatternMatchListBind(object):
    """Represents head and tail of a pattern-matched list (``head:tail``)."""
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail


# TODO: This must return an Either monad ;)
def pattern_match(value, pattern, env=None):
    """Pattern match a value and a pattern.

    :param value: the value to pattern-match on

    :param pattern: a pattern, consisting of literals and/or locally bound
                 variables

    :param env: a dictionary of local variables bound while matching

    :returns: (True, env) if the match is successful, and (False, env)
              otherwise

    :raises SyntaxError: if a variable name is used multiple times in the same
        pattern

    """
    from hask.hack import is_collection, nt_to_tuple
    env = {} if env is None else env
    if isinstance(pattern, PatternMatchBind):
        if pattern.name in env:
            msg = "Conflicting definitions for {}".format(pattern.name)
            raise SyntaxError(msg)
        else:
            env[pattern.name] = value
            return True, env
    elif isinstance(pattern, PatternMatchListBind):
        head, tail = list(value[:len(pattern.head)]), value[len(pattern.head):]
        matches, env = pattern_match(head, pattern.head, env)
        if matches:
            return pattern_match(tail, pattern.tail, env)
        else:
            return False, env
    elif type(value) == type(pattern):
        if isinstance(value, ADT):
            return pattern_match(nt_to_tuple(value), nt_to_tuple(pattern), env)
        elif is_collection(value):
            if len(value) != len(pattern):
                return False, env
            else:
                matches = []
                for v, p in zip(value, pattern):
                    match_status, env = pattern_match(v, p, env)
                    matches.append(match_status)
                return all(matches), env
        elif value == pattern:
            return True, env
        else:
            return False, env
    else:
        return False, env


del metaclass
