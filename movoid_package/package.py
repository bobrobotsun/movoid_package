#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : package
# Author        : Sun YiFan-Movoid
# Time          : 2024/9/17 16:37
# Description   : 
"""
from .for_import import get_root_path, python_path, import_module


class Package:
    def __init__(self, root_path=None):
        self.root_path = get_root_path(root_path, 2)
        python_path(self.root_path)
        self.old = {}

    def decorate_replace(self, package_name, object_name, decorator, args=None, kwargs=None, has_args=None):
        """
        对某个包内的元素进行装饰器
        :param package_name: 包名，str，从root的包路径
        :param object_name: 目标元素的名称，str，目标元素的类型可以是函数，也可以是类，但是需要自己对应好
        :param decorator: 装饰器，传元素本体
        :param args: 装饰器的args参数
        :param kwargs: 装饰器的kw参数
        :param has_args: 装饰器是否存在参数
        :return:
        """
        package = import_module(package_name)
        ori_object = getattr(package, object_name)
        self.old.setdefault((package.__name__, object_name), [])
        self.old[(package.__name__, object_name)].append(ori_object)
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

    def replace_object(self, package_name, object_name, new_object):
        """
        直接将某个元素替代为另一个元素
        :param package_name:
        :param object_name:
        :param new_object:
        :return:
        """
        package = import_module(package_name)
        ori_object = getattr(package, object_name)
        self.old.setdefault((package.__name__, object_name), [])
        self.old[(package.__name__, object_name)].append(ori_object)
        setattr(package, object_name, new_object)
