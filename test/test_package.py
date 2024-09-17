#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_package
# Author        : Sun YiFan-Movoid
# Time          : 2024/9/17 19:50
# Description   : 
"""
from movoid_package import importing
from .for_package.package1 import Package1
from movoid_function.decorator import wraps, decorate_class_function_exclude
from movoid_package.package import Package


def dec_package1(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.count += 1
        print('dec', self.count)
        return func(self, *args, **kwargs)

    return wrapper


class Test_Package:
    def test_class(self):
        a = importing('.for_package.package1')
        temp1 = Package1()
        temp1.package_function1()
        assert temp1.count == 0
        temp1.package_function2(1, 1, 2)
        assert temp1.count == 0

        Package.decorate_python('test.for_package.package1', 'Package1', decorate_class_function_exclude, [dec_package1])
        temp2 = Package1()
        temp2.package_function1()
        assert temp2.count == 1
        temp2.package_function2(1, 1, 2)
        assert temp2.count == 2
