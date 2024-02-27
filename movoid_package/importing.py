#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : importing
# Author        : Sun YiFan-Movoid
# Time          : 2024/2/28 0:01
# Description   : 
"""
import importlib
import inspect
import pathlib
import sys


def import_module(package_name: str):
    ori_file_name = inspect.stack()[-1].filename
    file_list = package_name.split('.')
    temp_file = pathlib.Path(ori_file_name)
    for i in file_list[:-1]:
        if i == '':
            temp_file = temp_file.parent
        else:
            temp_file = temp_file / i
    if not temp_file.is_dir():
        raise ImportError(f'{package_name} can not be found from {ori_file_name}')
    sys.path.insert(0, str(temp_file))
    temp_module = importlib.import_module(file_list[-1])
    setattr(temp_module, '__movoid_package__', package_name)
    return temp_module


def import_object(package_name: str, object_name: str):
    ori_file_name = inspect.stack()[-1].filename
    file_list = package_name.split('.')
    temp_file = pathlib.Path(ori_file_name)
    for i in file_list[:-1]:
        if i == '':
            temp_file = temp_file.parent
        else:
            temp_file = temp_file / i
    if not temp_file.is_dir():
        raise ImportError(f'{package_name} can not be found from {ori_file_name}')
    sys.path.insert(0, str(temp_file))
    temp_module = importlib.import_module(file_list[-1])
    if hasattr(temp_module, object_name):
        temp_object = getattr(temp_module, object_name)
    else:
        raise ImportError(f'there is no {object_name} in {package_name}')
    setattr(temp_object, '__movoid_package__', package_name)
    return temp_object
