#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : package
# Author        : Sun YiFan-Movoid
# Time          : 2024/9/17 16:37
# Description   : 
"""
import importlib
import pathlib


class Package:
    @classmethod
    def init(cls, root_path):
        temp_pathlib = pathlib.Path(root_path)
        if temp_pathlib.is_file():
            temp_pathlib = temp_pathlib.parent
        cls.root_path = temp_pathlib

    init(__file__)

    @classmethod
    def decorate_python(cls, package_name, object_name, decorator, args=None, kwargs=None, has_args=None):
        """
        用python的方法对某个包内的元素进行装饰器
        :param package_name: 包名，str，从root的包路径
        :param object_name: 目标元素的名称，str，目标元素的类型可以是函数，也可以是类，但是需要自己对应好
        :param decorator: 装饰器，传元素本体
        :param args: 装饰器的args参数
        :param kwargs: 装饰器的kw参数
        :param has_args: 装饰器是否存在参数
        :return:
        """
        package = importlib.import_module(package_name)
        ori_object = getattr(package, object_name)
        if has_args is None:
            if args is None and kwargs is None:
                has_args = False
            else:
                has_args = True
        else:
            has_args = bool(has_args)
        args = [] if args is None else list(args)
        kwargs = {} if kwargs is None else dict(kwargs)
        if has_args:
            now_object = decorator(*args, **kwargs)(ori_object)
        else:
            now_object = decorator(ori_object)
        setattr(package, object_name, now_object)

    @classmethod
    def import_package(cls, package_name: str):
        if package_name.startswith('.'):
            pass
        else:
            return importlib.import_module(package_name)
