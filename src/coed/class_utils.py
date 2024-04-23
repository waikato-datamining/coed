import os
import re
from setuptools import find_namespace_packages
from typing import Tuple, Any, List
import inspect
import importlib
from coed.serialization.objects import get_dict_reader

MODULE_CACHE = None
""" For caching the determine modules (list). """

CLASS_CACHE = None
""" For caching the determine class hierarchies (dict). """


def fix_module_name(module: str, cls: str) -> Tuple[str, str]:
    """
    Turns a.b._C.C into a.b.C if possible.

    :param module: the module
    :type module: str
    :param cls: the class name
    :type cls: str
    :return: the (potentially) updated tuple of module and class name
    """
    if module.split(".")[-1].startswith("_"):
        try:
            module_short = ".".join(module.split(".")[:-1])
            getattr(importlib.import_module(module_short), cls)
            module = module_short
        except Exception:
            pass
    return module, cls


def class_name_to_type(classname: str) -> Any:
    """
    Turns the class name into a type.

    :param classname: the class name to convert (a.b.Cls)
    :type classname: str
    :return: the type
    :rtype: type
    """
    p = classname.split(".")
    m = ".".join(p[:-1])
    c = p[-1]
    return getattr(importlib.import_module(m), c)


def get_class_name(o: Any) -> str:
    """
    Returns the classname of the object or type.

    :param o: the object or class to get the classname for
    :return: the classname (a.b.Cls)
    :rtype: str
    """
    if inspect.isclass(o):
        cls = o
    else:
        cls = type(o)
    m, c = fix_module_name(cls.__module__, cls.__name__)
    return m + "." + c


def find_module_names(use_cache: bool = True, module_regexp: str = None) -> List[str]:
    """
    Locates all module names used by shallowflow.

    :param use_cache: whether to use the cache or not
    :type use_cache: bool
    :param module_regexp: regular expression to limit the modules to search in
    :type module_regexp: str
    :return: the list of module names
    :rtype: list
    """
    global MODULE_CACHE

    result = []

    if not use_cache or (MODULE_CACHE is None):
        if MODULE_CACHE is None:
            MODULE_CACHE = list()

        location = inspect.getmodule(get_dict_reader).__file__
        # source?
        if "src/shallowflow" in location:
            location = location[0:location.index("src/shallowflow")]
            location = os.path.dirname(location)
            location = os.path.dirname(location)
        # installed
        else:
            while not location.endswith("shallowflow"):
                location = os.path.dirname(location)

        packages = find_namespace_packages(where=location)

        for package in packages:
            if ".src." in package:
                module_name = package[package.index(".src.") + 5:]
            else:
                module_name = "shallowflow." + package
            try:
                module = importlib.import_module(module_name)
                if module.__package__ not in result:
                    result.append(module.__package__)
            except Exception:
                pass
        result.sort()
        MODULE_CACHE = result[:]
    else:
        result = MODULE_CACHE[:]

    # limit result?
    if module_regexp is not None:
        regexp = re.compile(module_regexp)
        r = []
        for item in result:
            if regexp.match(item):
                r.append(item)
        result = r

    return result


def find_class_names(super_class: Any, use_cache: bool = True, module_regexp: str = None):
    """
    Finds all classes that are derived from the specified superclass in all the
    shallowflow modules.

    :param super_class: the class to look for
    :type super_class: type
    :param use_cache: whether to use the cache or not
    :type use_cache: bool
    :param module_regexp: regular expression to limit the modules to search in
    :type module_regexp: str
    :return: the list of class names
    :rtype: list
    """
    global CLASS_CACHE

    result = []
    module_names = find_module_names(use_cache=use_cache)

    locate = (not use_cache) or (CLASS_CACHE is None) or (super_class not in CLASS_CACHE)
    if CLASS_CACHE is None:
        CLASS_CACHE = dict()

    if locate:
        for module_name in module_names:
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, super_class):
                        module_name, c = fix_module_name(obj.__module__, obj.__name__)
                        result.append(module_name + "." + c)
            except Exception:
                pass
        result.sort()
        CLASS_CACHE[super_class] = result[:]
    else:
        result = CLASS_CACHE[super_class][:]

    # limit result?
    if module_regexp is not None:
        regexp = re.compile(module_regexp)
        r = []
        for item in result:
            if regexp.match(item):
                r.append(item)
        result = r

    return result


def find_classes(super_class: Any, use_cache: bool = True, module_regexp: str = None):
    """
    Finds all classes that are derived from the specified superclass in all the
    shallowflow modules.

    :param super_class: the class to look for
    :type super_class: type
    :param use_cache: whether to use the cache or not
    :type use_cache: bool
    :param module_regexp: regular expression to limit the modules to search in
    :type module_regexp: str
    :return: the list of classes
    :rtype: list
    """
    names = find_class_names(super_class, use_cache=use_cache, module_regexp=module_regexp)
    result = []
    for name in names:
        result.append(class_name_to_type(name))
    return result
