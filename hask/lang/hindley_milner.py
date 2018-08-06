'''Implementation of Hindley-Milner type inference system for Python.

Based on Robert Smallshire's implementation for OWL BASIC.  Robert's original
version can be found here:
http://smallshire.org.uk/sufficientlysmall/2010/04/11/a-hindley-milner-type-inference-implementation-in-python/

Changes from Robert's version:

1) Simplified type language somewhat (Let and Letrec are merged, as are Var
   and Ident)

2) Type system expanded to handle polymorphic higher-kinded types (however,
   in its current state it does not do this correctly due to the way that
   typeclasses were bolted on; this will be fixed in future versions)

3) Interface tweaked a bit to work better with Python types, including
   pretty-printing of type names and some useful subclasses of TypeOperator

4) Type unification also unifies typeclass constraints

'''

from __future__ import division, print_function, absolute_import

from xoutil.eight.abc import abstractmethod, ABC
from xoutil.objects import staticproperty


# Class definitions for the AST nodes which comprise the type language for
# which types will be inferred


class AST(ABC):
    '''A low-level Abstract Syntax Tree node in a typed lambda calculus.'''

    def __repr__(self):
        return str(self)

    @abstractmethod
    def analyze(self, env, non_generic=None):
        '''Computes the type of the expression given by node.

        The type of the node is computed in the context of the supplied type
        environment, ``env``.  Data types can be introduced into the language
        simply by having a predefined set of identifiers in the initial
        environment.  This way there is no need to change the syntax or, more
        importantly, the type-checking program when extending the language.

        :param self: The root of the Abstract Syntax Tree.

        :param env: The type environment is a mapping of expression identifier
                    names to type assignments.

        :param non_generic: A set of non-generic variables, or None.

        :returns: The computed type of the expression.

        :raises TypeError: The type of the expression could not be inferred,
             for example if it is not possible to unify two types such as
             Integer and Bool or if the Abstract Syntax Tree rooted at node
             (self) could not be parsed,

        '''


class Lam(AST):
    '''Lambda abstraction'''

    def __init__(self, v, body):
        self.v = v
        self.body = body

    def __str__(self):
        return "(\{v} -> {body})".format(v=self.v, body=self.body)

    def analyze(self, env, non_generic=None):
        if non_generic is None:
            non_generic = set()
        arg_type = TypeVariable()
        new_env = env.copy()
        new_env[self.v] = arg_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(arg_type)
        result_type = self.body.analyze(new_env, new_non_generic)
        return Function(arg_type, result_type)


class Var(AST):
    '''Variable/Identifier'''

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def analyze(self, env, non_generic=None):
        if non_generic is None:
            non_generic = set()
        return getType(self.name, env, non_generic)


class App(AST):
    '''Function application.

    An App node represents the application of a **single** argument.
    Functions over several arguments are curried.

    '''
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __str__(self):
        return "({fn} {arg})".format(fn=self.fn, arg=self.arg)

    def analyze(self, env, non_generic=None):
        if non_generic is None:
            non_generic = set()
        fun_type = self.fn.analyze(env, non_generic)
        arg_type = self.arg.analyze(env, non_generic)
        result_type = TypeVariable()
        unify(Function(arg_type, result_type), fun_type)
        return result_type


class Let(AST):
    '''Let binding (always recursive)'''

    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def __str__(self):
        exp = "(let {v} = {defn} in {body})"
        return exp.format(v=self.v, defn=self.defn, body=self.body)

    def analyze(self, env, non_generic=None):
        if non_generic is None:
            non_generic = set()
        new_type = TypeVariable()
        new_env = env.copy()
        new_env[self.v] = new_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(new_type)
        defn_type = self.defn.analyze(new_env, new_non_generic)
        unify(new_type, defn_type)
        return analyze(self.body, new_env, non_generic)


def show_type(type_name):
    '''Pretty-print a Python type or internal type name.

    :param type_name: a Python type, or a string representing a type name.

    :returns: a string representation of the type.

    '''
    if isinstance(type_name, str):
        return type_name
    elif isinstance(type_name, type):
        return type_name.__name__
    else:
        return str(type_name)


class TypeVariable(object):
    '''A type variable standing for an arbitrary type.

    All type variables have a unique id, but names are only assigned lazily,
    when required.

    Note that this approach is *not* thread-safe.

    '''

    __next_id = 0
    next_var_name = 'a'

    def __init__(self, constraints=()):
        self.id = TypeVariable._next_id
        self.instance = None
        self.__name = None
        self.constraints = constraints

    @property
    def name(self):
        '''Names are allocated to TypeVariables lazily.

        So that only those converted to strings are given names.

        '''
        if self.__name is None:
            # Reduce thread-safe risks
            cls = TypeVariable
            res, cls.next_var_name = (cls.next_var_name,
                                      chr(ord(cls.next_var_name) + 1))
            self.__name = res
        return self.__name

    @staticproperty
    def _next_id():
        # Reduce thread-safe risks
        res, TypeVariable.__next_id = (TypeVariable.__next_id,
                                       TypeVariable.__next_id + 1)
        return res

    def __str__(self):
        return str(self.instance) if self.instance is not None else self.name

    def __repr__(self):
        return "TypeVariable(id = {})".format(self.id)


class TypeOperator(object):
    '''An n-ary type constructor which builds a new type from old'''

    def __init__(self, name, types):
        self.name = name
        self.types = types

    def __str__(self):
        from itertools import chain
        return ' '.join(map(show_type, chain([self.name], self.types)))

    def __repr__(self):
        return str(self)


class Function(TypeOperator):
    '''A binary type constructor which builds function types'''

    def __init__(self, from_type, to_type):
        super(self.__class__, self).__init__("->", [from_type, to_type])

    def __str__(self):
        aux = (self.types[0], self.name, self.types[1])
        return ' '.join(map(show_type, aux))


class Tuple(TypeOperator):
    '''N-ary constructor which builds tuple types'''

    def __init__(self, types):
        super(self.__class__, self).__init__(tuple, types)

    def __str__(self):
        return "({})".format(", ".join(map(show_type, self.types)))


class ListType(TypeOperator):
    '''Unary constructor which builds list types'''

    def __init__(self, list_type):
        super(self.__class__, self).__init__("[]", [list_type])

    def __str__(self):
        return "[{}]".format(show_type(self.types[0]))


def analyze(node, env, non_generic=None):
    '''Use ``node.analyze(env, non_generic)``.'''
    return node.analyze(env, non_generic)


def getType(name, env, non_generic):
    '''Get the type of identifier name from the type environment env.

    :param name: The identifier name

    :param env: The type environment mapping from identifier names to types

    :param non_generic: A set of non-generic TypeVariables

    :raises ParseError: Raised if name is an undefined symbol in the type
            environment.

    '''
    try:
        return fresh(env[name], non_generic)
    except KeyError:
        # XXX: Use ``from ...`` in Python 3
        raise TypeError("Undefined symbol {}".format(name))


def fresh(t, non_generic):
    '''Makes a copy of a type expression.

    The type ``t`` is copied.  The the generic variables are duplicated and
    the ``non_generic`` variables are shared.

    :param t: A type to be copied.

    :param non_generic: A set of non-generic TypeVariables

    '''
    mappings = {}  # A mapping of TypeVariables to TypeVariables

    def freshrec(tp):
        p = prune(tp)
        if isinstance(p, TypeVariable):
            if isGeneric(p, non_generic):
                if p not in mappings:
                    mappings[p] = TypeVariable()
                return mappings[p]
            else:
                return p
        elif isinstance(p, TypeOperator):
            return TypeOperator(p.name, [freshrec(x) for x in p.types])

    return freshrec(t)


def unify_var(v1, t2):
    '''Unify the type variable `v1` and the type `t2`.

    i.e. makes their types the same and unifies typeclass constraints.

    Note: Must be called with v1 and t2 pre-pruned

    :param v1: The type variable to be made equivalent

    :param t2: The second type to be be equivalent

    Instead of returning, modify `v1` and `t2` to add the unification as a
    constraint.

    :raises TypeError: Raised if the types cannot be unified.

    '''
    if v1 != t2:
        if isinstance(t2, TypeVariable):
            # unify typeclass constraints
            union = tuple(set(v1.constraints + t2.constraints))
            v1.constraints = union
            t2.constraints = union
        if not occursInType(v1, t2):
            v1.instance = t2
        else:
            raise TypeError("recursive unification")


def unify(t1, t2):
    '''Unify the two types t1 and t2.  Makes the types t1 and t2 the same.

    Note that the current method of unifying higher-kinded types does not
    properly handle kind, i.e. it will happily unify `f a` and `g b c`.
    This is due to the way that typeclasses are implemented, and will be fixed
    in future versions.

    :param t1: The first type to be made equivalent.

    :param t2: The second type to be be equivalent.

    Modify `t1` and `t2` in-place, by modifying their constraints for the
    unification.

    :raises TypeError: Raised if the types cannot be unified.

    '''
    a = prune(t1)
    b = prune(t2)
    if isinstance(a, TypeVariable):
        unify_var(a, b)
    elif isinstance(a, TypeOperator) and isinstance(b, TypeVariable):
        unify_var(b, a)
    elif isinstance(a, TypeOperator) and isinstance(b, TypeOperator):
        # Unify polymorphic higher-kinded type
        if isinstance(a.name, TypeVariable) and len(a.types) > 0:
            a.name = b.name
            a.types = b.types
            unify(a, b)
        elif isinstance(b.name, TypeVariable):
            unify(b, a)
        # Unify concrete higher-kinded type
        elif (a.name != b.name or len(a.types) != len(b.types)):
            raise TypeError("Type mismatch: {} != {}".format(a, b))
        for p, q in zip(a.types, b.types):
            unify(p, q)
    else:
        raise TypeError("Not unified")


def prune(t):
    '''Returns the currently defining instance of t.

    As a side effect, collapses the list of type instances.  The function
    prune is used whenever a type expression has to be inspected: it will
    always return a type expression which is either an uninstantiated type
    variable or a type operator; i.e. it will skip instantiated variables, and
    will actually prune them from expressions to remove long chains of
    instantiated variables.

    :param t: The type to be pruned

    :returns: An uninstantiated TypeVariable or a TypeOperator

    '''
    if isinstance(t, TypeVariable):
        if t.instance is not None:
            t.instance = prune(t.instance)
            return t.instance
    return t


def isGeneric(v, non_generic):
    '''Checks whether a given variable occurs in non-generic variables.

    Note that a variable in such a list may be instantiated to a type term, in
    which case the variables contained in the type term are considered
    non-generic.

    .. note:: Must be called with `v` pre-pruned

    :param v: The TypeVariable to be tested for genericity.

    :param non_generic: A set of non-generic TypeVariables.

    :returns: True if v is a generic variable, otherwise False.

    '''
    return not occursIn(v, non_generic)


def occursInType(v, type2):
    '''Checks whether a type variable occurs in a type expression.

    .. note:: Must be called with v pre-pruned

    :param v:  The TypeVariable to be tested for.

    :param type2: The type in which to search.

    :returns: True if v occurs in type2, otherwise False.

    '''
    pruned_type2 = prune(type2)
    if pruned_type2 == v:
        return True
    elif isinstance(pruned_type2, TypeOperator):
        return occursIn(v, pruned_type2.types)
    else:
        return False


def occursIn(t, types):
    '''Checks whether a types variable occurs in any other types.

    :param v:  The TypeVariable to be tested for.

    :param types: The sequence of types in which to search.

    :returns: True if t occurs in any of types, otherwise False.

    '''
    return any(occursInType(t, t2) for t2 in types)
