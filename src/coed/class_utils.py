import importlib
import inspect
from typing import Tuple, Any


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
