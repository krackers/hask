from hask3.lang.syntax import sig
from hask3.lang.syntax import H
from hask3.lang.syntax import t
from hask3.lang.syntax import instance
from hask3.lang import List
from hask3.Data.Functor import fmap
from hask3.Control.Applicative import Applicative


class Monad(Applicative):
    """Basic operations over a monad.

    Monad is a concept from a branch of mathematics known as Category Theory.
    From the perspective of a Haskell programmer, however, it is best to think
    of a monad as an abstract datatype of actions.

    Dependencies:

    - `~hask3.Control.Applicative.Applicative`:class:

    Attributes:

    - ``bind``
    - ``__rshift__``

    Minimal complete definition:

    - ``bind``

    """
    @classmethod
    def make_instance(typeclass, cls, bind):
        from hask3.hack import is_builtin
        from hask3.lang.type_system import build_instance
        from hask3.lang.syntax import H, t
        bind = bind ** (H[Monad, "m"]/
                        t("m", "a") >> (H/ "a" >> t("m", "b")) >> t("m", "b"))
        if not is_builtin(cls):
            def bind_wrap(s, o):
                return Monad[s].bind(s, o)
            cls.__rshift__ = bind_wrap
        build_instance(Monad, cls, {"bind": bind})


@sig(H[Monad, "m"]/ t("m", "a") >> (H/ "a" >> t("m", "b")) >> t("m", "b"))
def bind(m, fn):
    """``bind :: Monad m => m a -> (a -> m b) -> m b``

    Monadic bind.

    """
    return Monad[m].bind(m, fn)


@sig(H[Monad, "m"]/ t("m", t("m", "a")) >> t("m", "a"))
def join(m):
    """``join :: Monad m => m (m a) -> m a``

    The join function is the conventional monad join operator.  It is used to
    remove one level of monadic structure, projecting its bound argument into
    the outer level.

    """
    from hask3.Prelude import id
    return bind(m, id)


@sig(H[Monad, "m"]/ (H/ "a" >> "r") >> t("m", "a") >> t("m", "r"))
def liftM(fn, m):
    """``liftM :: Monad m => (a1 -> r) -> m a1 -> m r``

    Promote a function to a monad.

    """
    return fmap(fn, m)


@sig(H[(Monad, 'm')]/ (H/ 'a' >> t('m', 'b')) >> (H/ 'b' >> t('m', 'c')) >>
     'a' >> t('m', 'c'))
def kleisli_fish(f, g, x):
    '''``(>=>) :: Monad m => (a -> m b) -> (b -> m c) -> a -> m c``
    '''
    return bind(f(x), g)


@sig(H[(Monad, 'm')]/ (H/ 'b' >> t('m', 'c')) >> (H/ 'a' >> t('m', 'b')) >>
     'a' >> t('m', 'c'))
def kleisli_compose(g, f, x):
    '''``(>=>) :: Monad m => (b -> m c) -> (a -> m b) -> a -> m c``
    '''
    return bind(f(x), g)


def _list_bind(x, fn):
    from itertools import chain
    from hask3.lang import L
    return L[chain.from_iterable(fmap(fn, x))]


instance(Monad, List).where(
    bind = _list_bind
)


del _list_bind, Applicative, List, instance, t, H, sig
