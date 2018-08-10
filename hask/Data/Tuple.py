from __future__ import division, print_function, absolute_import

from hask.lang.syntax import sig
from hask.lang.syntax import H


@sig(H/ ("a", "b") >> "a")
def fst(tup):
    """``fst :: (a, b) -> a``

    Extract the first component of a pair.

    """
    x, _y = tup
    return x


@sig(H/ ("a", "b") >> "b")
def snd(tup):
    """``snd :: (a, b) -> b``

    Extract the second component of a pair.

    """
    _x, y = tup
    return y


@sig(H/ (H/ ("a", "b") >> "c") >> "a" >> "b" >> "c")
def curry(tup_fn, x, y):
    """``curry :: ((a, b) -> c) -> a -> b -> c``

    Converts an uncurried function to a curried function.

    """
    return tup_fn((x, y))


@sig(H/ (H/ "a" >> "b" >> "c") >> ("a", "b") >> "c")
def uncurry(fn, tup):
    """``uncurry :: (a -> b -> c) -> (a, b) -> c``

    Converts a curried function to a function on pairs.

    """
    return fn(fst(tup), snd(tup))


@sig(H/ ("a", "b") >> ("b", "a"))
def swap(tup):
    """``swap :: (a, b) -> (b, a)``

    Swap the components of a pair.

    """
    a, b = tup
    return (b, a)


del sig, H
