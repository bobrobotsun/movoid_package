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


def get_root_path(root_path=None) -> pathlib.Path:
    """
    获得root path。如果不输入，那么就根据当前文件的__name__来判断root path。如果输入，则根据输入的路径来生成root path
    :param root_path: 不输入就按照默认生成，输入则必须是已经存在的路径或文件
    :return: pathlib.Path
    """
    temp_path = None
    if root_path is not None:
        temp_path = pathlib.Path(root_path).absolute()
        if not temp_path.exists():
            temp_path = None
    if temp_path is None:
        temp_path = pathlib.Path(__file__).absolute()
        if __name__ != '__main__':
            name_list = __name__.split('.')
            if temp_path.stem == '__init__':
                temp_path = temp_path.parent
            temp_path = temp_path.parents[len(name_list) - 1]
    if temp_path.is_file():
        re_path = temp_path.parent
    else:
        re_path = temp_path
    return re_path


def import_module(package_name: str, object_name=None):
    """
    使用文本的方式选择包并导入
    :param package_name: 包名，可以任意地使用相对路径或绝对路径
    :param object_name: 如果只想导入该包地某个对象，那就输入对象的名称。输入None就是全包导入
    :return: 生成的包/对象返回
    """
    if package_name.startswith('.'):
        root_path = get_root_path(None)
        temp_path = pathlib.Path(__file__).absolute()
        while package_name.startswith('.'):
            temp_path = temp_path.parent
            package_name = package_name[1:]
        root_len = len(root_path.parents)
        package_len = len(temp_path.parents)
        if package_len == root_len:
            if temp_path != root_path:
                raise ImportError(f'向上追溯的路径{temp_path}和root路径{root_path}不同')
        elif package_len > root_len:
            if temp_path.parents[package_len - root_len - 1] == root_path:
                folder_list = [_.stem for _ in temp_path.parents[:package_len - root_len]]
                package_name = '.'.join([*folder_list[::-1], package_name])
            else:
                raise ImportError(f'向上追溯的路径{temp_path}不在root路径{root_path}下')
        else:
            raise ImportError(f'向上追溯的路径{temp_path}已经高于{root_path}了')
    temp_module = importlib.import_module(package_name)
    if object_name is None:
        return temp_module
    else:
        object_name = str(object_name)
        if hasattr(temp_module, object_name):
            return getattr(temp_module, object_name)
        else:
            raise ImportError(f'{package_name}不存在对象{object_name}')


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


print(__name__)
