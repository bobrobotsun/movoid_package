#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : importing
# Author        : Sun YiFan-Movoid
# Time          : 2024/2/28 0:01
# Description   : 
"""
import importlib.machinery
import importlib.util
import importlib
import inspect
import pathlib
import sys
from typing import Union


def importing(package_name: str, object_name: Union[str, None] = None):
    """
    you can import anything by this function with normal format
    :param package_name: relative routine to target package
    :param object_name: if import package ,this is None. if import object, this is object name
    :return: target package or object
    """
    ori_file_name = inspect.stack()[1].filename
    file_list = package_name.split('.')
    temp_file = pathlib.Path(ori_file_name)
    for i in file_list[:-1]:
        if i == '':
            temp_file = temp_file.parent
        else:
            temp_file = temp_file / i
    sys.path.insert(0, str(temp_file))
    temp_module = importlib.import_module(file_list[-1])
    sys.path.pop(0)
    if object_name is None:
        setattr(temp_module, '__movoid_package__', ['importing', [package_name], file_list[-1]])
        return temp_module
    else:
        if hasattr(temp_module, object_name):
            temp_object = getattr(temp_module, object_name)
            setattr(temp_object, '__movoid_package__', ['importing', [package_name, object_name], object_name])
            return temp_object
        else:
            raise ImportError(f'there is no {object_name} in {temp_module}')


def path_importing(package_path: str, package_name=None, object_name: Union[str, None] = None):
    """
    if you want to import a package with a path str,you can use this instead of import
    :param package_path: target package file path should with suffix.
    :param package_name: 如果文件有一个的路径，建议输入，可以保证相对路径的导入没有错误
    :param object_name: if import package ,this is None. if import object, this is object name
    :return: target package or object
    """
    file_path = pathlib.Path(package_path)
    if not pathlib.Path(package_path).is_file():
        raise FileNotFoundError(f'{file_path} is not a file.')
    package_name = file_path.stem if package_name is None else str(package_name)
    loader = importlib.machinery.SourceFileLoader(package_name, package_path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    temp_module = importlib.util.module_from_spec(spec)
    loader.exec_module(temp_module)
    if object_name is None:
        setattr(temp_module, '__movoid_package__', ['path_importing', [package_path], file_path.stem])
        return temp_module
    else:
        if hasattr(temp_module, object_name):
            temp_object = getattr(temp_module, object_name)
            setattr(temp_object, '__movoid_package__', ['path_importing', [package_path, object_name], object_name])
            return temp_object
        else:
            raise ImportError(f'there is no {object_name} in {temp_module}')
