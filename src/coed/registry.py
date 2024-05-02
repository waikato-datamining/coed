import importlib
import inspect
import os
import sys
import traceback
from typing import Callable, Union, List, Optional, Type

from pkg_resources import working_set

from .class_utils import get_class_name, class_name_to_type

DEFAULT = "DEFAULT"
""" the placeholder for the default class listers in the environment variable. """

LIST_CLASSES = "list_classes"
""" the default method for listing classes. """


def get_class_lister(class_lister: str) -> Callable:
    """
    Parses the class_lister definition and returns the function.
    The default format is "module_name:function_name".
    If ":function_name" is omitted it is assumed to be ":list_classes".

    :param class_lister: the class lister definition to parse
    :type class_lister: str
    :return: the parsed function
    """
    if ":" not in class_lister:
        module_name = class_lister
        func_name = LIST_CLASSES
    else:
        module_name, func_name = class_lister.split(":")

    try:
        module = importlib.import_module(module_name)
    except:
        raise Exception("Failed to import class lister module: %s" % module_name)

    if hasattr(module, func_name):
        func = getattr(module, func_name)
        if inspect.isfunction(func):
            return func
        else:
            raise Exception("Class lister function is not an actual function: %s" % class_lister)
    else:
        raise Exception("Class lister function '%s' not found in module '%s'!" % (func_name, module_name))


class Registry:
    """
    Registry for managing class hierarchies.
    """

    def __init__(self, default_class_listers: Union[str, List[str]] = None, env_class_listers: str = None,
                 excluded_class_listers: Union[str, List[str]] = None, env_excluded_class_listers: str = None):
        """
        Initializes the registry.

        :param default_class_listers: the default class lister(s) to use
        :type default_class_listers: str or list
        :param env_class_listers: the environment variable to retrieve the class lister(s) from
        :type env_class_listers: str
        :param excluded_class_listers: the class lister(s) to exclude from being used
        :type excluded_class_listers: str or list
        :param env_excluded_class_listers: the environmenr variable to retrieve the excluded class lister(s) from
        :type env_excluded_class_listers: str
        """

        self._classes = dict()
        self._default_class_listers = None
        self._env_class_listers = None
        self._excluded_class_listers = None
        self._env_excluded_class_listers = None
        self._custom_class_listers = None

        self.default_class_listers = default_class_listers
        self.env_class_listers = env_class_listers
        self.excluded_class_listers = excluded_class_listers
        self.env_excluded_class_listers = env_excluded_class_listers

    @property
    def default_class_listers(self) -> Optional[List[str]]:
        """
        Returns the class lister functions.

        :return: the functions
        :rtype: list
        """
        return self._default_class_listers

    @default_class_listers.setter
    def default_class_listers(self, class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the class lister functions to use. Clears the class cache.

        :param class_listers: the list of class listers to use, None to unset
        :type class_listers: list
        """
        if class_listers is None:
            class_listers = ""
        if isinstance(class_listers, str):
            class_listers = [x.strip() for x in class_listers.split(",")]
        elif isinstance(class_listers, list):
            class_listers = class_listers[:]
        else:
            raise Exception("default_class_listers must be either str or list, but got: %s" % str(type(class_listers)))
        self._default_class_listers = class_listers
        self._classes = dict()

    @property
    def env_class_listers(self) -> Optional[str]:
        """
        Returns the environment variable with the class lister functions (if any).

        :return: the class lister functions, None if none set
        :rtype: str
        """
        return self._env_class_listers

    @env_class_listers.setter
    def env_class_listers(self, class_listers: Optional[str]):
        """
        Sets/unsets the environment variable with the class lister functions to use. Clears the class cache.

        :param class_listers: the environment variable with the class lister functions to use, None to unset
        :type class_listers: str
        """
        self._env_class_listers = class_listers
        self._classes = dict()

    @property
    def excluded_class_listers(self) -> Optional[List[str]]:
        """
        Returns the excluded class lister functions.

        :return: the functions
        :rtype: list
        """
        return self._excluded_class_listers

    @excluded_class_listers.setter
    def excluded_class_listers(self, excluded_class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the excluded class lister functions to use. Clears the class cache.

        :param excluded_class_listers: the list of excluded class listers to use, None to unset
        :type excluded_class_listers: list
        """
        if excluded_class_listers is None:
            excluded_class_listers = ""
        if isinstance(excluded_class_listers, str):
            excluded_class_listers = [x.strip() for x in excluded_class_listers.split(",")]
        elif isinstance(excluded_class_listers, list):
            excluded_class_listers = excluded_class_listers[:]
        else:
            raise Exception("excluded_class_listers must be either str or list, but got: %s" % str(type(excluded_class_listers)))
        self._excluded_class_listers = excluded_class_listers
        self._classes = dict()

    @property
    def env_excluded_class_listers(self) -> Optional[str]:
        """
        Returns the environment variable with the excluded class lister functions (if any).

        :return: the excluded class lister functions, None if none set
        :rtype: str
        """
        return self._env_excluded_class_listers

    @env_excluded_class_listers.setter
    def env_excluded_class_listers(self, excluded_class_listers: Optional[str]):
        """
        Sets/unsets the environment variable with the excluded class lister functions to use. Clears the class cache.

        :param excluded_class_listers: the environment variable with the excluded class lister functions to use, None to unset
        :type excluded_class_listers: str
        """
        self._env_excluded_class_listers = excluded_class_listers
        self._classes = dict()

    @property
    def custom_class_listers(self) -> Optional[List[str]]:
        """
        Returns the custom class listers (if any).

        :return: the class listers, None if none set
        :rtype: list
        """
        return self._custom_class_listers

    @custom_class_listers.setter
    def custom_class_listers(self, class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the custom class listers to use. Clears the plugin cache.

        :param class_listers: the list of class listers to use, None to unset
        :type class_listers: list
        """
        self._custom_class_listers = class_listers
        self._classes = dict()

    def has_env_class_listers(self) -> bool:
        """
        Checks whether an environment variable for class listers is set.

        :return: True if set
        :rtype: bool
        """
        return (self._env_class_listers is not None) \
               and (len(self._env_class_listers) > 0) \
               and (os.getenv(self._env_class_listers) is not None) \
               and (len(os.getenv(self._env_class_listers)) > 0)

    def has_env_excluded_class_listers(self) -> bool:
        """
        Checks whether an environment variable for excluded class listers is set.

        :return: True if set
        :rtype: bool
        """
        return (self._env_excluded_class_listers is not None) \
               and (len(self._env_excluded_class_listers) > 0) \
               and (os.getenv(self._env_excluded_class_listers) is not None) \
               and (len(os.getenv(self._env_excluded_class_listers)) > 0)

    def _expand_default_class_listers_placeholder(self, c: str) -> str:
        """
        Expands the DEFAULT class listers placeholder in the comma-separated class listers string.

        :param c: the class listers string to expand
        :type c: str
        :return: the expanded class listers string
        :rtype: str
        """
        if DEFAULT in c:
            if len(self.default_class_listers) > 0:
                c = c.replace(DEFAULT, ",".join(self.default_class_listers))
            else:
                c = c.replace(DEFAULT, "")
        return c

    def actual_fallback_class_listers(self) -> List[str]:
        """
        Returns list the of class listers to fall back on.
        Precedence: custom_class_listers > env_class_listers > default_class_listers

        :return: the list of class listers
        :rtype: list
        """
        if (self._custom_class_listers is not None) and (len(self._custom_class_listers) > 0):
            return self._custom_class_listers

        if self.has_env_class_listers():
            m = self._expand_default_class_listers_placeholder(os.getenv(self.env_class_listers))
            return [x.strip() for x in m.split(",")]

        return self.default_class_listers[:]

    def actual_excluded_class_listers(self) -> List[str]:
        """
        Returns list the of excluded class listers.
        Precedence: excluded_env_class_listers > excluded_class_listers

        :return: the list of class listers
        :rtype: list
        """
        if self.has_env_excluded_class_listers():
            m = self._expand_default_class_listers_placeholder(os.getenv(self._env_excluded_class_listers))
            return [x.strip() for x in m.split(",")]

        return self.excluded_class_listers[:]

    def _determine_sub_classes(self, cls: Type, module_name: str) -> List[str]:
        """
        Determines all the sub-classes of type cls in the specified module.

        :param cls: the superclass
        :param module_name: the module to look for sub-classes
        :type module_name: str
        :return: the list of sub-classes
        :rtype: list
        """
        result = []

        try:
            module = importlib.import_module(module_name)
        except:
            print("Failed to import module: %s" % module_name, file=sys.stderr)
            traceback.print_exc()
            return result

        for att_name in dir(module):
            if att_name.startswith("_"):
                continue
            if att_name.startswith("Abstract"):
                continue
            att = getattr(module, att_name)
            if inspect.isclass(att) and not inspect.isabstract(att) and issubclass(att, cls):
                try:
                    obj = att()
                except NotImplementedError:
                    pass
                except:
                    print("Problem encountered instantiating: %s" % (module_name + "." + att_name), file=sys.stderr)
                    traceback.print_exc()
                    continue
                result.append(get_class_name(att))

        return result

    def _determine_from_class_listers(self, c: str, class_listers: List[str]) -> List[str]:
        """
        Determines the derived classes via the specified class listers.

        :param c: the superclass to get the classes for
        :type c: str
        :param class_listers: the class lister functions to use
        :type class_listers: list
        :return: the determined list of subclasses
        :rtype: list
        """
        result = []

        if len(class_listers) > 0:
            try:
                cls = class_name_to_type(c)
            except:
                print("Failed to instantiate class: %s" % c, file=sys.stderr)
                traceback.print_exc()
                return result

            for class_lister in class_listers:
                try:
                    func = get_class_lister(class_lister)
                except:
                    print("Problem encountered with class lister: %s" % class_lister, file=sys.stderr)
                    traceback.print_exc()
                    continue

                if self.excluded_class_listers is not None:
                    if class_lister in self.excluded_class_listers:
                        continue

                if inspect.isfunction(func):
                    class_dict = func()
                    if c in class_dict:
                        for sub_module in class_dict[c]:
                            sub_classes = self._determine_sub_classes(cls, sub_module)
                            result.extend(sub_classes)

        return result

    def _determine_from_entry_points(self, c: str) -> List[str]:
        """
        Determines the derived classes via class listers defined as entry points.

        :param c: the superclass to get the classes for
        :type c: str
        :return: the determined list of subclasses
        :rtype: list
        """
        result = []
        class_listers = []
        for item in working_set.iter_entry_points("class_lister", None):
            # format: "name=module:function",
            class_listers.append(item.module_name + ":" + item.attrs[0])
        if len(class_listers) > 0:
            result = self._determine_from_class_listers(c, class_listers)
        return result

    def _determine_from_env(self, c: str) -> List[str]:
        """
        Determines the derived classes via class listers defined through the environment variable.

        :param c: the superclass to get the classes for
        :type c: str
        :return: the determined list of subclasses
        :rtype: list
        """
        result = []

        if os.getenv(self.env_class_listers) is not None:
            # format: "module:function,module:function,...",
            class_listers = os.getenv(self.env_class_listers).split(",")
            result = self._determine_from_class_listers(c, class_listers)

        return result

    def _initialize(self, c: str):
        """
        Initializes the class cache for the specified superclass.

        :param c: the superclass to initialize the cache for
        :type c: str
        :return: the list of classes for the superclass
        :rtype: list
        """
        all_classes = set()

        # from entry points
        entry_point_classes = self._determine_from_entry_points(c)
        if entry_point_classes is not None:
            all_classes.update(entry_point_classes)

        # register from class listers as well?
        if (len(all_classes) == 0) or ((self._custom_class_listers is not None) and (len(self._custom_class_listers) > 0)) or self.has_env_class_listers():
            actual = self.actual_fallback_class_listers()
            for excl in self.actual_excluded_class_listers():
                if excl in actual:
                    actual.remove(excl)
            all_classes.update(self._determine_from_class_listers(c, actual))

        self._classes[c] = sorted(list(all_classes))

    def classes(self, c: Union[str, Type], fail_if_empty: bool = True) -> List[str]:
        """
        Returns the classes for the specified superclass.

        :param c: the super class to get the derived classes for (classname or type)
        :param fail_if_empty: whether to raise an exception if no classes present
        :type fail_if_empty: bool
        :return: the list of classes
        :rtype: list
        """
        if not isinstance(c, str):
            c = get_class_name(c)
        if c not in self._classes:
            self._initialize(c)
        result = []
        if c in self._classes:
            result = self._classes[c]
        if fail_if_empty and (len(result) == 0):
            raise Exception("No classes found for: %s" % c)
        return result
