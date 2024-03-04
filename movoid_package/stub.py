#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : stub
# Author        : Sun YiFan-Movoid
# Time          : 2024/3/2 20:19
# Description   : 
"""
import importlib.machinery
import importlib.util
import inspect
import pathlib
import typing
from typing import List, Callable, Any, Union


class Stub:
    def __init__(self, file_path: str, encoding: str = 'utf8'):
        self._file_path = pathlib.Path(file_path)
        self._encoding = encoding
        self._stub_path = self._file_path.with_suffix('.pyi')
        self._stub_file = None
        self._module = None
        self._members = {}
        self._imports = {}
        self._from_imports = {}
        self._movoid_package = []
        self._movoid_path_import = {}
        self._stubs_strings = []
        self.init()

    def init(self):
        if not self._file_path.is_file():
            raise FileNotFoundError(f'{self._file_path} is not a file.')
        self._stub_file = self._stub_path.open(mode='w', encoding=self._encoding)
        loader = importlib.machinery.SourceFileLoader('imported', str(self._file_path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        self._module = module
        self._members = {key: item for key, item in module.__dict__.items() if (not key.startswith('__') and inspect.getmodule(item) is None)}
        self._imports = {key: item for key, item in module.__dict__.items() if inspect.ismodule(item) and not hasattr(item, '__movoid_package__')}
        self._from_imports = {}
        self._movoid_package = {key: getattr(item, '__movoid_package__') for key, item in module.__dict__.items() if hasattr(item, '__movoid_package__')}
        self._stubs_strings: List[str] = []

        for package_name, movoid_package in self._movoid_package.items():
            func = movoid_package[0]
            if func == 'importing':
                if len(movoid_package[1]) == 1:
                    packages = movoid_package[1][0].split('.')
                    parent_package = '.'.join(packages[:-1])
                    if packages[-2] == '':
                        parent_package += '.'
                    this_package = packages[-1]
                else:
                    parent_package = movoid_package[1][0]
                    this_package = movoid_package[1][1]
                if this_package == package_name:
                    this_import = f'{this_package}'
                else:
                    this_import = f'{this_package} as {package_name}'
                if parent_package not in self._from_imports:
                    self._from_imports[parent_package] = []
                    if this_import not in self._from_imports[parent_package]:
                        self._from_imports[parent_package].append(this_import)
            else:
                if 'movoid_package' not in self._from_imports:
                    self._from_imports['movoid_package'] = []
                if func not in self._from_imports['movoid_package']:
                    self._from_imports['movoid_package'].append(func)
                self._movoid_path_import[package_name] = movoid_package

        for key, item in self._members.items():
            if inspect.isclass(item):
                self._stubs_strings.append(self._generate_class_stub(key, item))
            elif inspect.isfunction(item):
                self._stubs_strings.append(self._function_stub_string(key, item))
            elif not inspect.ismodule(item):
                self._stubs_strings.append(self._object_stub_string(key, item))
        self.print('#' * 50)
        self.print('# This is auto generated by code.')
        self.print('#' * 50 + '\n')
        for name, package in self._imports.items():
            self.print(f'import {name}')
        for package, target in self._from_imports.items():
            self.print(f'from {package} import {", ".join(target)}')
        self.print('')
        for package_name, (import_func, import_args, import_name) in self._movoid_path_import.items():
            arg_text = ', '.join([f'r"{_}"' for _ in import_args])
            self.print(f'{package_name} = {import_func}({arg_text})')
        for stubs in self._stubs_strings:
            self.print(stubs)
        self._stub_file.close()

    def print(self, *args, sep=' ', end='\n'):
        print(*args, sep=sep, end=end, file=self._stub_file, flush=True)

    def _get_element_name_with_module(self, element: Union[type, Any]) -> str:
        # The element can be a string, for example "def f() -> 'SameClass':..."
        if isinstance(element, str):
            return element
        elif isinstance(element, type):
            module = inspect.getmodule(element)
            if module is None or module.__name__ == 'builtins' or module.__name__ == '__main__' or hasattr(element, '__movoid_package__'):
                return element.__name__
            else:
                module_name = module.__name__
                if module_name not in self._imports:
                    self._imports.setdefault(module_name, module)
                return '{0}.{1}'.format(module_name, element.__name__)
        elif inspect.getmodule(element) == inspect.getmodule(typing):
            module_name = str(element).split('.')[0]
            if module_name not in self._imports:
                self._imports.setdefault('')
            return str(element).replace('NoneType', 'None')

    def _generate_class_stub(self, class_name: str, tar_class: type) -> str:
        parent_class = [self._get_element_name_with_module(_) for _ in tar_class.__bases__]
        if tar_class.__class__ != type:
            parent_class.append('metaclass=' + self._get_element_name_with_module(tar_class.__class__))
        retext = 'class ' + class_name.split('.')[-1] + '(' + ', '.join(parent_class) + '):\n'

        object_class = {
            'function': [],
            'object': []
        }

        for key, element in tar_class.__dict__.items():
            if inspect.isfunction(element):
                object_class['function'].append(key)
            elif not inspect.ismodule(element) and not key.startswith('__'):
                object_class['object'].append(key)
        for key in object_class['object']:
            element = tar_class.__dict__[key]
            retext += '\t' + self._object_stub_string(key, element) + '\n'
        for key in object_class['function']:
            element = tar_class.__dict__[key]
            retext += self._function_stub_string(key, element, indentation='\t')

        retext += '\t...\n'

        return retext

    def _exploit_annotation(self, anno: Any, starting: str = ': ') -> str:
        annotation_string = ''
        if anno != inspect.Parameter.empty:
            annotation_string += starting + self._get_element_name_with_module(anno)
        return annotation_string

    def _function_stub_string(self, func_name: str, tar_func: Callable, indentation: str = '') -> str:
        sign = inspect.signature(tar_func)
        re_text = f'{indentation}def {func_name}('
        for i, (par_name, parameter) in enumerate(sign.parameters.items()):
            annotation = self._exploit_annotation(parameter.annotation)
            default = ''
            if parameter.default != parameter.empty and type(parameter.default).__module__ == 'builtins' and not str(parameter.default).startswith('<'):
                if isinstance(parameter.default, str):
                    temp_str = parameter.default.replace("'", "\\'")
                    default = f' = \'{temp_str}\''
                else:
                    temp_str = str(parameter.default)
                    default = f' = {temp_str}'

            re_text += par_name + annotation + default

            if i < len(sign.parameters) - 1:
                re_text += ', '
        ret_annotation = self._exploit_annotation(sign.return_annotation, starting=' -> ')
        re_text += f'){ret_annotation}:'

        if tar_func.__doc__ is not None:
            re_text += '\n' + indentation + '\t"""\n'
            for line in tar_func.__doc__.split('\n')[1:-1]:
                re_text += indentation + '\t' + line.strip().rstrip() + '\n'
            re_text += indentation + '\t"""\n' + indentation + '\t...\n'
        else:
            re_text += '\t...\n'
        return re_text

    def _object_stub_string(self, object_name: str, object_itself: Any) -> str:
        return f'{object_name}: {self._get_element_name_with_module(type(object_itself))}'