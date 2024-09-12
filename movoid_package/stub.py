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
import re
import sys
import traceback
import typing
from typing import List, Callable, Any, Union


class Stub:
    def __init__(self, file_path: str, package_name=None, root_dir=None, encoding: str = 'utf8'):
        self._file_path = pathlib.Path(file_path).absolute()
        self._package_name = 'imported'
        self.calculate_package_name(file_path, package_name, root_dir)
        self._encoding = encoding
        self._stub_path = self._file_path.with_suffix('.pyi')
        self._stub_file = None
        self._module = None
        self._members = {}
        self._other_members = {}
        self._imports = {}
        self._from_imports = {}
        self._movoid_package = []
        self._movoid_path_import = {}
        self._stubs_strings = []
        self._class_init_variable = {}
        self.init()

    def calculate_package_name(self, file_path, package_name, root_dir):
        if root_dir is None:
            if package_name is None:
                package_name = 'imported'
            else:
                package_name = str(package_name)
        else:
            root_pathlib = pathlib.Path(root_dir).absolute()
            file_pathlib = pathlib.Path(file_path).absolute()
            root_layer = len(root_pathlib.parents)
            file_layer = len(file_pathlib.parents)
            package_list = []
            if file_layer > root_layer and file_pathlib.parents[file_layer - root_layer - 1] == root_pathlib:
                if file_pathlib.stem == '__init__':
                    file_pathlib = file_pathlib.parent
                for i in range(root_layer, len(file_pathlib.parents)):
                    package_list.insert(0, file_pathlib.stem)
                    file_pathlib = file_pathlib.parent
                package_name = '.'.join(package_list)
            else:
                if package_name is None:
                    package_name = 'imported'
                else:
                    package_name = str(package_name)
        self._package_name = package_name

    def init(self):
        if not self._file_path.is_file():
            raise FileNotFoundError(f'{self._file_path} is not a file.')
        self._stub_file = self._stub_path.open(mode='w', encoding=self._encoding)
        loader = importlib.machinery.SourceFileLoader(self._package_name, str(self._file_path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        self._module = module
        self._members = {key: item for key, item in module.__dict__.items() if (not key.startswith('__') and inspect.getmodule(item) is None)}
        self._imports = {key: item for key, item in module.__dict__.items() if inspect.ismodule(item) and not hasattr(item, '__movoid_package__')}
        self._other_members = {key: item for key, item in module.__dict__.items() if (not key.startswith('__') and inspect.getmodule(item) is not None)}
        self._from_imports = {}
        self._movoid_package = {key: getattr(item, '__movoid_package__') for key, item in module.__dict__.items() if hasattr(item, '__movoid_package__')}
        self._stubs_strings: List[str] = []
        self._read_class_init_variable()

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
            element_str = str(element)
            module_name = element_str.split('.')[0]
            if module_name not in self._imports:
                self._imports.setdefault(module_name, typing)
            element_re = re.search(r'(.*?)\[(.*)]', element_str)
            if element_re is not None:
                arg_list = [self._get_element_name_with_module(_) for _ in element.__args__]
                element_str = f'{element_re.group(1)}[{", ".join(arg_list)}]'
            return element_str.replace('NoneType', 'None')

    def _generate_class_stub(self, class_name: str, tar_class: type) -> str:
        parent_class = [self._get_element_name_with_module(_) for _ in tar_class.__bases__]
        if tar_class.__class__ != type:
            parent_class.append('metaclass=' + self._get_element_name_with_module(tar_class.__class__))
        pure_class_name = class_name.split('.')[-1]
        retext = 'class ' + pure_class_name + '(' + ', '.join(parent_class) + '):\n'

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
            content = '...'
            if key == '__init__' and pure_class_name in self._class_init_variable:
                if self._class_init_variable[pure_class_name]['super'] or self._class_init_variable[pure_class_name]['self']:
                    content = []
                    if self._class_init_variable[pure_class_name]['super']:
                        content.append(self._class_init_variable[pure_class_name]['super'])
                    if self._class_init_variable[pure_class_name]['self']:
                        for _self_text in self._class_init_variable[pure_class_name]['self']:
                            for _name, _class in self._other_members.items():
                                package_name = inspect.getmodule(_class).__name__
                                full_name = f'{package_name}.{_name}' if inspect.isclass(_class) else _name
                                class_list = _self_text[2].split('.')
                                try_full_class_str = '.'.join(class_list[:-1])
                                try_single_class = class_list[0]
                                if _self_text[2] == _name:
                                    self._from_imports.setdefault(package_name, [])
                                    self._from_imports[package_name].append(_name)
                                    break
                                elif _self_text[2] == full_name:
                                    self._imports.setdefault(full_name, _class)
                                    break
                                elif try_full_class_str == _name:
                                    self._from_imports.setdefault(package_name, [])
                                    self._from_imports[package_name].append(_name)
                                    break
                                elif try_full_class_str == full_name:
                                    self._imports.setdefault(full_name, _class)
                                    break
                                elif try_single_class == _name:
                                    self._imports.setdefault(try_full_class_str, _class)
                                    break
                            else:
                                try:
                                    try_type = eval('typing.' + _self_text[2])
                                    if inspect.getmodule(try_type) == inspect.getmodule(typing):
                                        _self_text[2] = 'typing.' + _self_text[2]
                                except Exception:
                                    try:
                                        try_type = eval(_self_text[2])
                                        if inspect.getmodule(try_type) == inspect.getmodule(typing):
                                            _self_text[2] = _self_text[2]
                                    except Exception:
                                        print(f'we do not know what is {_self_text[2]}', file=sys.stderr)
                                        traceback.print_exc()

                            content.append(f'{_self_text[1]}: {_self_text[2]} = {_self_text[3]}')
            element = tar_class.__dict__[key]
            retext += self._function_stub_string(key, element, indentation='\t', content=content)

        retext += '\t...\n'

        return retext

    def _read_class_init_variable(self):
        with self._file_path.open(mode='r', encoding=self._encoding) as file:
            file_text = file.read()
            class_text = re.findall(r'\nclass (.*?)(\(|:)((.|\s)*?)(\n\S|$)', file_text)
            for class_one in class_text:
                class_name = class_one[0]
                init_re = re.search(r'\n(\t| {4})def __init__((.|\s)*?)(\n(\t| {4})\S|$)', class_one[2])
                if init_re:
                    init_text = init_re.group(2)
                    super_text = re.search(r'\n(\t| {4}){2}(super.*)', init_text).group(2)
                    self_text = [list(_) for _ in re.findall(r'\n(\t| {4}){2}(self\..*?):(.*?)=(.*)', init_text)]
                    for _i in self_text:
                        _i[2] = _i[2].strip(' ')
                    self._class_init_variable[class_name] = {'super': super_text, 'self': self_text}

    def _exploit_annotation(self, anno: Any, starting: str = ': ') -> str:
        annotation_string = ''
        if anno != inspect.Parameter.empty:
            annotation_string += starting + self._get_element_name_with_module(anno)
        return annotation_string

    def _function_stub_string(self, func_name: str, tar_func: Callable, indentation: str = '', content: Union[str, List[str]] = '...') -> str:
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

        if isinstance(content, list):
            content_text = ''.join(['\n\t' + indentation + _ for _ in content])
        else:
            content_text = '\t' + content

        if tar_func.__doc__ is not None:
            re_text += '\n' + indentation + '\t"""\n'
            for line in tar_func.__doc__.split('\n')[1:-1]:
                re_text += indentation + '\t' + line.strip().rstrip() + '\n'
            re_text += indentation + '\t"""\n' + indentation + f'{content_text}\n'
        else:
            re_text += f'{content_text}\n'
        return re_text

    def _object_stub_string(self, object_name: str, object_itself: Any) -> str:
        return f'{object_name}: {self._get_element_name_with_module(type(object_itself))}'
