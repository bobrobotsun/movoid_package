#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : package
# Author        : Sun YiFan-Movoid
# Time          : 2024/9/17 16:37
# Description   : 
"""
from .for_import import _get_root_path, python_path, import_module


class Package:
    def __init__(self, root_path=None):
        self.root_path = _get_root_path(root_path)
        python_path(self.root_path)

    def decorate_python(self, package_name, object_name, decorator, args=None, kwargs=None, has_args=None):
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
        package = import_module(package_name)
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

    def analyse_dict(self, ori_dict: dict) -> dict:
        if 'type' in ori_dict:
            _type = ori_dict['type']
            if _type == 'import':
                re_value = import_module(ori_dict['package'], ori_dict.get('object', None))
            else:
                re_value = None
        else:
            re_value = ori_dict
            for k, v in ori_dict.items():
                if isinstance(v, list):
                    re_value[k] = self.analyse_list(v)
                elif isinstance(v, dict):
                    re_value[k] = self.analyse_dict(v)
                else:
                    re_value[k] = v
        return re_value

    def analyse_list(self, ori_list: list) -> list:
        re_value = []
        for i, v in enumerate(ori_list):
            if isinstance(v, list):
                re_value.append(self.analyse_list(v))
            elif isinstance(v, dict):
                re_value.append(self.analyse_dict(v))
            else:
                re_value.append(v)
        return re_value

    def decorate_dict(self, tar_dict: dict):
        tar_dict = self.analyse_dict(tar_dict)
        self.decorate_python(**tar_dict)
