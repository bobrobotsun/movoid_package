#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test1
# Author        : Sun YiFan-Movoid
# Time          : 2024/3/4 22:56
# Description   : 
"""

import math
from movoid_package import importing as im, path_importing as pim

# tests = im('.test2')
# func2 = im('.test2', 'func2')
# func3 = pim(rf'E:\000develop\movoid_package\test\test2.py', 'func2')


class Test:
    att1 = 1

    def func1(self, a, b=1):
        pass


class Test2(Test):
    att2 = 'asdf'

    def func2(self, c, d=1):
        """
        this is doc
        :param c:
        :param d:
        :return:
        """
        pass


class_test2 = Test2()
print(Test2.att1.__class__)
print(class_test2.att1)
