#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import unittest

from hask import L, H, sig
from hask.Control.Monad import kleisli_fish, kleisli_compose


class TestKleisliArrows(unittest.TestCase):
    def test_kleisli_fish(self):
        @sig(H/ int >> [int])
        def numbers(n):
            return L[0, ..., n]

        @sig(H/ int >> [int])
        def odds(n):
            return L[(x for x in numbers(n) if x % 2)]

        on1 = kleisli_fish(numbers, odds)
        on2 = kleisli_compose(odds, numbers)

        assert list(on1(10)) == list(on2(10))
