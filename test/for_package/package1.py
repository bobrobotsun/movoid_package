#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : package1
# Author        : Sun YiFan-Movoid
# Time          : 2024/9/17 17:06
# Description   : 
"""


class Package1:
    def __init__(self):
        self.dict = {}
        self.count = 0

    def package_function1(self):
        return 1

    def package_function2(self, a, b, c=1):
        return a, b, c + 1
