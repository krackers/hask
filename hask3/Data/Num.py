import sys
import math

from hask3.lang.syntax import data
from hask3.lang.syntax import d
from hask3.lang.syntax import deriving
from hask3.lang.syntax import instance

from hask3.lang.syntax import H
from hask3.lang.syntax import sig
from hask3.lang.syntax import t

from hask3.lang.lazylist import Enum
from hask3.lang.typeclasses import Show
from hask3.Data.Eq import Eq
from hask3.Data.Ord import Ord


class Num(Show, Eq):
    """Basic numeric class.

    Dependencies:

    - `~hask3.lang.typeclasses.Show`:class:
    - `~hask3.lang.typeclasses.Eq`:class:

    Attributes:

    - ``__add__``
    - ``__mul__``
    - ``__abs__``
    - ``signum``
    - ``fromInteger``
    - ``__neg__``
    - ``__sub__``

    Minimal complete definition:

    - ``add``
    - ``mul``
    - ``abs``
    - ``signum``
    - ``fromInteger``
    - ``negate``

    """
    @classmethod
    def make_instance(typeclass, cls, add, mul, abs, signum, fromInteger,
                      negate, sub=None):
        from hask3.lang.syntax import H, sig
        from hask3.lang.type_system import build_instance

        @sig(H[(Num, "a")]/ "a" >> "a" >> "a")
        def default_sub(a, b):
            return a.__add__(b.__neg__())

        sub = default_sub if sub is None else sub
        attrs = {"add": add, "mul": mul, "abs": abs, "signum": signum,
                 "fromInteger": fromInteger, "negate": negate, "sub": sub}

        build_instance(Num, cls, attrs)


@sig(H[(Num, "a")]/ "a" >> "a")
def negate(a):
    """``signum :: Num a => a -> a``

    Unary negation.

    """
    return Num[a].negate(a)


@sig(H[(Num, "a")]/ "a" >> "a")
def signum(a):
    """``signum :: Num a => a -> a``

    Sign of a number. The functions abs and signum should satisfy the law:
    abs x * signum x == x
    For real numbers, the signum is either -1 (negative), 0 (zero) or 1
    (positive).

    """
    return Num[a].signum(a)


@sig(H[(Num, "a")]/ "a" >> "a")
def abs(a):
    """``abs :: Num a => a -> a``

    Absolute value.

    """
    return Num[a].abs(a)


instance(Num, int).where(
    add = int.__add__,
    mul = int.__mul__,
    abs = int.__abs__,
    signum = lambda x: -1 if x < 0 else (1 if x > 0 else 0),
    fromInteger = int,
    negate = int.__neg__,
    sub = int.__sub__
)

instance(Num, float).where(
    add = float.__add__,
    mul = float.__mul__,
    abs = float.__abs__,
    signum = lambda x: -1.0 if x < 0.0 else (1.0 if x > 0.0 else 0.0),
    fromInteger = float,
    negate = float.__neg__,
    sub = float.__sub__
)

instance(Num, complex).where(
    add = complex.__add__,
    mul = complex.__mul__,
    abs = complex.__abs__,
    signum = lambda x: complex(-1) if x < 0 else complex(1 if x > 0 else 0),
    fromInteger = complex,
    negate = complex.__neg__,
    sub = complex.__sub__
)


class Fractional(Num):
    """Fractional numbers, supporting real division.

    Dependencies:

    - `Num`:class:

    Attributes:

    - ``fromRational``
    - ``recip``
    - ``__div__``

    Minimal complete definition:

    - ``fromRational``
    - ``div``

    """
    @classmethod
    def make_instance(typeclass, cls, fromRational, div, recip=None):
        from hask3.lang.type_system import build_instance
        if recip is None:
            recip = lambda x: div(1, x)
        attrs = {"fromRational": fromRational, "div": div, "recip": recip}
        build_instance(Fractional, cls, attrs)


Ratio, R = (
        data.Ratio("a") == d.R("a", "a") & deriving(Eq)
)


Rational = t(Ratio, int)


instance(Fractional, float).where(
    fromRational = lambda rat: float(rat[0])/float(rat[1]),
    div = lambda a, b: float(a)/float(b),
    recip = lambda x: 1.0/x
)


@sig(H[(Fractional, "a")]/ "a" >> "a")
def recip(a):
    """``recip :: Fractional a => a -> a``

    Reciprocal fraction.

    """
    return Fractional[a].recip(a)


class Floating(Fractional):
    """Trigonometric and hyperbolic functions and related functions.

    Dependencies:

    - `Fractional`:class:

    Attributes:

    - ``pi``
    - ``exp``
    - ``sqrt``
    - ``log``
    - ``pow``
    - ``logBase``
    - ``sin``
    - ``tan``
    - ``cos``
    - ``asin``
    - ``atan``
    - ``acos``
    - ``sinh``
    - ``tanh``
    - ``cosh``
    - ``asinh``
    - ``atanh``
    - ``acosh``

    Minimal complete definition:

    - ``pi``
    - ``exp``
    - ``sqrt``
    - ``log``
    - ``pow``
    - ``logBase``
    - ``sin``
    - ``tan``
    - ``cos``
    - ``asin``
    - ``atan``
    - ``acos``
    - ``sinh``
    - ``tanh``
    - ``cosh``
    - ``asinh``
    - ``atanh``
    - ``acosh``

    """
    @classmethod
    def make_instance(typeclass, cls, pi, exp, sqrt, log, pow, logBase, sin,
                      tan, cos, asin, atan, acos, sinh, tanh, cosh, asinh,
                      atanh, acosh):
        from hask3.lang.type_system import build_instance
        attrs = {"pi": pi, "exp": exp, "sqrt": sqrt, "log": log, "pow": pow,
                "logBase": logBase, "sin": sin, "tan": tan, "cos": cos,
                "asin": asin, "atan": atan, "acos": acos, "sinh": sinh,
                "tanh": tanh, "cosh": cosh, "asinh": asinh, "atanh": atanh,
                "acosh": acosh}
        build_instance(Floating, cls, attrs)


@sig(H[(Floating, "a")]/ "a" >> "a")
def exp(x):
    """``exp :: Floating a => a -> a``

    """
    return Floating[x].exp(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def sqrt(x):
    """``sqrt :: Floating a => a -> a``

    """
    return Floating[x].sqrt(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def log(x):
    """``log:: Floating a => a -> a``

    """
    return Floating[x].log(x)


@sig(H[(Floating, "a")]/ "a" >> "a" >> "a")
def pow(x, y):
    """``pow :: Floating a => a -> a -> a``

    """
    return Floating[x].pow(x, y)


@sig(H[(Floating, "a")]/ "a" >> "a" >> "a")
def logBase(x, b):
    """
    ``logBase :: Floating a => a -> a -> a``
    """
    return Floating[x].logBase(x, b)


@sig(H[(Floating, "a")]/ "a" >> "a")
def sin(x):
    """
    ``sin :: Floating a => a -> a``
    """
    return Floating[x].sin(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def cos(x):
    """
    ``cos :: Floating a => a -> a``
    """
    return Floating[x].cos(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def tan(x):
    """
    ``tan :: Floating a => a -> a``
    """
    return Floating[x].tan(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def asin(x):
    """
    ``asin :: Floating a => a -> a``
    """
    return Floating[x].asin(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def atan(x):
    """
    ``atan :: Floating a => a -> a``
    """
    return Floating[x].atan(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def acos(x):
    """
    ``acos :: Floating a => a -> a``
    """
    return Floating[x].acos(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def sinh(x):
    """
    ``sinh :: Floating a => a -> a``
    """
    return Floating[x].sinh(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def tanh(x):
    """
    ``tanh :: Floating a => a -> a``
    """
    return Floating[x].tanh(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def cosh(x):
    """
    ``cosh :: Floating a => a -> a``
    """
    return Floating[x].cosh(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def asinh(x):
    """``asinh :: Floating a => a -> a``

    """
    return Floating[x].asinh(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def atanh(x):
    """
    ``atanh :: Floating a => a -> a``
    """
    return Floating[x].atanh(x)


@sig(H[(Floating, "a")]/ "a" >> "a")
def acosh(x):
    """
    ``acosh :: Floating a => a -> a``
    """
    return Floating[x].acosh(x)


instance(Floating, float).where(
    pi = math.pi,
    exp = math.exp,
    sqrt = math.sqrt,
    log = math.log,
    pow = pow,
    logBase = math.log,
    sin = math.sin,
    tan = math.tan,
    cos = math.cos,
    asin = math.asin,
    atan = math.atan,
    acos = math.acos,
    sinh = math.sinh,
    tanh = math.tanh,
    cosh = math.cosh,
    asinh = math.asinh,
    atanh = math.atanh,
    acosh = math.acosh
)


class Real(Num, Ord):
    """Real numbers.

    Dependencies:

    - `Num`:class:
    - `~hask3.lang.typeclasses.Ord`:class:

    Attributes:

    - ``toRational``

    Minimal complete definition:

    - ``toRational``

    """
    @classmethod
    def make_instance(typeclass, cls, toRational):
        from hask3.lang.type_system import build_instance
        build_instance(Real, cls, {})


@sig(H[(Real, "a")]/ "a" >> Rational)
def toRational(x):
    """``toRational :: Real a => a -> Rational``

    Conversion to Rational.

    """
    return Real[x].toRational(x)


class Integral(Real, Enum):
    """Integral numbers, supporting integer division.

    Dependencies:

    - `Real`:class:
    - `~hask3.lang.lazylist.Enum`:class:

    Attributes:

    - ``quotRem``
    - ``toInteger``
    - ``quot``
    - ``rem``
    - ``div``
    - ``mod``

    Minimal complete definition:

    - ``quotRem``
    - ``toInteger``
    - ``quot``
    - ``rem``
    - ``div``
    - ``mod``

    """
    @classmethod
    def make_instance(typeclass, cls, quotRem, divMod, toInteger, quot=None,
                      rem=None, div=None, mod=None):
        from hask3.lang.type_system import build_instance

        quot = lambda x: quotRem(x)[0] if quot is None else quot
        rem = lambda x: quotRem(x)[1] if rem is None else rem
        div = lambda x: divMod(x)[0] if div is None else div
        mod = lambda x: divMod(x)[1] if mod is None else mod

        attrs = {"quotRem": quotRem, "toInteger": toInteger, "quot": quot,
                 "rem": rem, "div": div, "mod": mod, "divMod": divMod}
        build_instance(Integral, cls, attrs)


@sig(H[(Integral, "a")]/ "a" >> "a" >> t(Ratio, "a"))
def toRatio(num, denom):
    """``toRatio :: Integral a => a -> a -> Ratio a``

    Conversion to Ratio.

    """
    import fractions
    frac = fractions.Fraction(num, denom)
    return R(frac.numerator, frac.denominator)


instance(Real, int).where(
    toRational = lambda x: toRatio(x, 1)
)

instance(Real, float).where(
    toRational = lambda x: toRatio(round(x), 1)  # obviously incorrect
)

instance(Integral, int).where(
    quotRem = lambda x, y: (x / y, x % y),
    toInteger = int,
    quot = lambda a, b: int(a)/int(b),
    rem = int.__mod__,
    div = lambda a, b: int(a)/int(b),
    mod = int.__mod__,
    divMod = divmod
)


class RealFrac(Real, Fractional):
    """Extracting components of fractions.

    Dependencies:

    - `Real`:class:
    - `Fractional`:class:

    Attributes:

    - ``properFraction``
    - ``truncate``
    - ``round``
    - ``ceiling``
    - ``floor``

    Minimal complete definition:

    - ``properFraction``
    - ``truncate``
    - ``round``
    - ``ceiling``
    - ``floor``

    """
    @classmethod
    def make_instance(typeclass, cls, properFraction, truncate, round,
                      ceiling, floor):
        from hask3.lang.type_system import build_instance
        attrs = {"properFraction": properFraction, "truncate": truncate,
                "round": round, "ceiling": ceiling, "floor": floor}
        build_instance(RealFrac, cls, attrs)


@sig(H[(RealFrac, "a"), (Integral, "b")]/ "a" >> ("b", "a"))
def properFraction(x):
    """``properFraction :: RealFrac a, Integral b => a -> (b, a)``

    The function properFraction takes a real fractional number x and returns a
    pair (n,f) such that x = n+f, and:

        n is an integral number with the same sign as x; and
        f is a fraction with the same type and sign as x, and with absolute
        value less than 1.

    """
    return RealFrac[x].properFraction(x)


@sig(H[(RealFrac, "a"), (Integral, "b")]/ "a" >> "b")
def truncate(x):
    """``truncate :: RealFrac a, Integral b => a -> b``

    truncate(x) returns the integer nearest x between zero and x

    """
    return RealFrac[x].truncate(x)


@sig(H[(RealFrac, "a"), (Integral, "b")]/ "a" >> "b")
def round(x):
    """``round :: RealFrac a, Integral b => a -> b``

    round(x) returns the nearest integer to x; the even integer if x is
    equidistant between two integers

    """
    return RealFrac[x].round(x)


@sig(H[(RealFrac, "a"), (Integral, "b")]/ "a" >> "b")
def ceiling(x):
    """``ceiling :: RealFrac a, Integral b => a -> b``

    ceiling(x) returns the least integer not less than x

    """
    return RealFrac[x].ceiling(x)


@sig(H[(RealFrac, "a"), (Integral, "b")]/ "a" >> "b")
def floor(x):
    """``floor :: RealFrac a, Integral b => a -> b``

    floor(x) returns the greatest integer not greater than x

    """
    return RealFrac[x].floor(x)


def _properFraction(x):
    import math
    return int(math.floor(x)), x - math.floor(x)


def _truncate(x):
    import math
    return int(math.floor(x) if x > 0 else math.floor(x+1))


instance(RealFrac, float).where(
    properFraction = _properFraction,
    truncate = _truncate,
    round = lambda x: int(round(x, 0)),
    ceiling = math.ceil,
    floor = math.floor
)


class RealFloat(Floating, RealFrac):
    """Efficient, machine-independent access to the components of a
    floating-point number.

    Dependencies:

    - `Floating`:class:
    - `RealFrac`:class:

    Attributes:

    - ``floatRange``
    - ``isNan``
    - ``isInfinite``
    - ``isNegativeZero``
    - ``atan2``

    Minimal complete definition:

    - ``floatRange``
    - ``isNan``
    - ``isInfinite``
    - ``isNegativeZero``
    - ``atan2``

    """
    @classmethod
    def make_instance(typeclass, cls, floatRange, isNan, isInfinite,
                      isNegativeZero, atan2):
        from hask3.lang.type_system import build_instance
        attrs = {"floatRange": floatRange, "isNan": isNan,
                "isInfinite": isInfinite, "isNegativeZero": isNegativeZero,
                "atan2": atan2}
        build_instance(RealFloat, cls, attrs)


@sig(H[(RealFloat, "a")]/ "a" >> bool)
def isNaN(x):
    """``isNaN :: RealFloat a => a -> bool``

    True if the argument is an IEEE "not-a-number" (NaN) value

    """
    return RealFloat[x].isNan(x)


@sig(H[(RealFloat, "a")]/ "a" >> bool)
def isInfinite(x):
    """``isInfinite :: RealFloat a => a -> bool``

    True if the argument is an IEEE infinity or negative infinity

    """
    return RealFloat[x].isInfinite(x)


@sig(H[(RealFloat, "a")]/ "a" >> bool)
def isNegativeZero(x):
    """``isNegativeZero :: RealFloat a => a -> bool``

    True if the argument is an IEEE negative zero

    """
    return RealFloat[x].isNegativeZero(x)


@sig(H[(RealFloat, "a")]/ "a" >> "a" >> "a")
def atan2(y, x):
    """``atan2 :: RealFloat a => a -> a -> a``

    a version of arctangent taking two real floating-point arguments

    """
    return RealFloat[x].atan2(y, x)


def _isNegativeZero(x):
    import math
    return math.copysign(1, x) == -1.0


instance(RealFloat, float).where(
    floatRange = (sys.float_info.min, sys.float_info.max),
    isNan = math.isnan,
    isInfinite = lambda x: x == float('inf') or x == -float('inf'),
    isNegativeZero = _isNegativeZero,
    atan2 = math.atan2
)


del math, sys
del data, d, deriving, instance
del H, sig, t
del Enum, Show, Eq, Ord
