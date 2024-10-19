#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_for_import
# Author        : Sun YiFan-Movoid
# Time          : 2024/10/19 21:33
# Description   : 
"""
import pathlib

from movoid_package import get_root_path


def func1(index=2):
    return get_root_path(trace_index=index)


class Test_For_Import:
    def test_for_import(self):
        assert pathlib.Path(func1(2)) == pathlib.Path('.').resolve()
