# flake8: noqa: F401

import unittest

from hask3 import __


class TestPrelude(unittest.TestCase):

    def test_imports(self):
        """
        Prelude imports from Data.* modules; ensure things get loaded correctly
        """
        from hask3.Prelude import fst, snd, curry, uncurry
        from hask3.Prelude import lines, words, unlines, unwords
        from hask3.Prelude import Maybe, Just, Nothing, maybe
        from hask3.Prelude import Either, Left, Right, either
        from hask3.Prelude import Ordering, LT, EQ, GT, max, min, compare
        from hask3.Prelude import Num, abs, negate, subtract
        from hask3.Prelude import Fractional, recip
        from hask3.Prelude import Integral, toRatio, Ratio, R, Rational
        from hask3.Prelude import Floating, exp, sqrt, log, pow, logBase, sin
        from hask3.Prelude import tan, cos, asin, atan, acos, sinh, tanh, cosh
        from hask3.Prelude import asinh, atanh, acosh
        from hask3.Prelude import Real, toRational
        from hask3.Prelude import RealFrac, properFraction, truncate, round
        from hask3.Prelude import ceiling, floor
        from hask3.Prelude import RealFloat, isNaN, isInfinite, isNegativeZero
        from hask3.Prelude import atan2

        # Data.List, Data.Foldable
        from hask3.Prelude import map, filter, head, last, tail, init, null
        from hask3.Prelude import length, reverse, foldl, foldl1, foldr
        from hask3.Prelude import foldr1, and_, or_, any, all, sum, product
        from hask3.Prelude import concat, concatMap, maximum, minimum, scanl
        from hask3.Prelude import scanl1, scanr, scanr1, iterate, repeat
        from hask3.Prelude import replicate, cycle, take, drop, splitAt
        from hask3.Prelude import takeWhile, dropWhile, span, break_, elem
        from hask3.Prelude import notElem, lookup, zip, zip3, unzip, unzip3
        from hask3.Prelude import zipWith, zipWith3

    def test_functions(self):
        from hask3.Prelude import subtract, even, odd, gcd, lcm, id, const, flip
        from hask3.Prelude import until, asTypeOf, error

        self.assertEqual(5, subtract(2, 7))
        self.assertEqual(-5, subtract(7, 2))
        self.assertTrue(even(20) and even(-20))
        self.assertFalse(even(21) and even(-21))
        self.assertTrue(odd(21) and odd(-21))
        self.assertFalse(odd(20) and odd(-20))
        self.assertEqual(4, gcd(8, 12))
        self.assertEqual(4, gcd(8, 12))
        self.assertEqual(2, gcd(-4, 6))
        self.assertEqual(8, gcd(8, 0))
        self.assertEqual(8, gcd(0, 8))
        self.assertEqual(0, gcd(0, 0))
        self.assertEqual(12, lcm(6, 4))
        self.assertEqual(3, lcm(3, 3))
        self.assertEqual(9, lcm(9, 3))
        self.assertEqual(2, lcm(1, 2))
        self.assertEqual(0, lcm(0, 8))
        self.assertEqual(0, lcm(8, 0))
        self.assertEqual(0, lcm(0, 0))

        self.assertEqual("a", id("a"))
        self.assertEqual("a", id * id * id % "a")
        self.assertEqual(1, const(1, 2))
        self.assertEqual(1, const(1) * const(3) % "a")
        self.assertEqual(1, flip(__-__, 2, 3))
        self.assertEqual(1, flip(const, 2, 1))
        self.assertEqual(2, flip(flip(const))(2, 1))

        self.assertEqual(1, until(__>0, __+1, -20))
        self.assertEqual(-20, until(__<0, __+1, -20))
        self.assertEqual("a", asTypeOf("a", "a"))
        self.assertEqual(1, asTypeOf(1, 1))

        # error
        with self.assertRaises(Exception):
            error("")
        msg = "OUT OF CHEESE ERROR"
        try:
            error(msg)
        except Exception as e:
            self.assertEqual((msg, ), e.args)
