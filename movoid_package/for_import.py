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
from typing import Union


def get_root_path(root_path=None, trace_index: int = 1) -> pathlib.Path:
    """
    获得root path。如果不输入，那么就根据当前文件的__name__来判断root path。如果输入，则根据输入的路径来生成root path
    :param root_path: 不输入就按照默认生成，输入则必须是已经存在的路径或文件
    :param trace_index: 如果相对路径的导入，那么往前追溯多少，一般如果是直接调用，那么1是合理的，每多嵌套一层，就建议+1
    :return: pathlib.Path
    """
    temp_path = None
    if root_path is not None:
        temp_path = pathlib.Path(root_path).absolute().resolve()
        if not temp_path.exists():
            temp_path = None
    if temp_path is None:
        trace_item = inspect.stack()[trace_index]
        temp_path = pathlib.Path(trace_item.filename).absolute().resolve()
        trace_name = trace_item.frame.f_globals['__name__']
        if trace_name != '__main__':
            name_list = trace_name.split('.')
            if temp_path.stem == '__init__':
                temp_path = temp_path.parent
            temp_path = temp_path.parents[len(name_list) - 1]
    if temp_path.is_file():
        re_path = temp_path.parent
    else:
        re_path = temp_path
    return re_path


def _get_object_from_module(module, object_name: Union[str, None] = None, error_text: str = ''):
    if object_name is None:
        return module
    else:
        object_name = str(object_name)
        if hasattr(module, object_name):
            return getattr(module, object_name)
        else:
            raise ImportError(f'{error_text}不存在对象{object_name}')


def python_path(root_path):
    root_pathlib = pathlib.Path(root_path).absolute().resolve()
    for i in sys.path:
        if root_pathlib == pathlib.Path(i):
            break
    else:
        sys.path.insert(0, str(root_pathlib))


def import_module(package_name: str, object_name: Union[str, None] = None, trace_index: int = 1):
    """
    使用文本的方式选择包并导入
    :param package_name: 包名，可以任意地使用相对路径或绝对路径
    :param object_name: 如果只想导入该包地某个对象，那就输入对象的名称。输入None就是全包导入
    :param trace_index: 如果相对路径的导入，那么往前追溯多少，一般如果是直接调用，那么1是合理的，每多嵌套一层，就建议+1
    :return: 生成的包/对象返回
    """
    if package_name.startswith('.'):
        root_path = get_root_path(None, trace_index)
        temp_path = pathlib.Path(inspect.stack()[trace_index].filename).absolute().resolve()
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
                folder_list = [_.stem for _ in list(temp_path.parents)[:package_len - root_len - 1]]
                package_name = '.'.join([*folder_list[::-1], temp_path.stem, package_name])
            else:
                raise ImportError(f'向上追溯的路径{temp_path}不在root路径{root_path}下')
        else:
            raise ImportError(f'向上追溯的路径{temp_path}已经高于root路径{root_path}了')
    temp_module = importlib.import_module(package_name)
    return _get_object_from_module(temp_module, object_name, package_name)


def import_module_by_path(package_path: str, root_path=None, object_name: Union[str, None] = None, trace_index: int = 1):
    """
    通过文件名导入module，需要输入root路径，如果没有就按照当前的root路径寻找包路径。
    :param package_path: 待导入的package的路径
    :param root_path: root path的路径，默认用当前程序的root path
    :param object_name: 对象名称，不输入则导入整个包
    :param trace_index: 如果相对路径的导入，那么往前追溯多少，一般如果是直接调用，那么1是合理的，每多嵌套一层，就建议+1
    :return: 导入的包
    """
    root_path = get_root_path(root_path, trace_index)
    package_pathlib = pathlib.Path(package_path).absolute().resolve()
    if not (package_pathlib.exists() and package_pathlib.is_file()):
        raise ImportError(f'{package_pathlib}不是一个有效的文件')
    package_len = len(package_pathlib.parents)
    root_len = len(root_path.parents)
    if package_len > root_len:
        if package_pathlib.parents[package_len - root_len - 1] == root_path:
            folder_list = [_.stem for _ in list(package_pathlib.parents)[:package_len - root_len - 1]]
            if package_pathlib.stem != '__init__':
                folder_list.insert(0, package_pathlib.stem)
            package_name = '.'.join(folder_list[::-1])
        else:
            raise ImportError(f'目标文件{package_pathlib}不在root路径{root_path}下')
    else:
        raise ImportError(f'目标路径{package_path}已经高于root路径{root_path}了')
    python_path(root_path)
    temp_module = importlib.import_module(package_name)
    return _get_object_from_module(temp_module, object_name, str(package_pathlib))
