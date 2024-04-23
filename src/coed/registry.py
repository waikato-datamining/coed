import abc
import importlib
import inspect
import os
import sys
import traceback
from typing import List, Union, Optional, Type

from pkg_resources import working_set

from .class_utils import get_class_name, class_name_to_type


class Registry:
    """
    Registry for managing class hierarchies.
    """

    def __init__(self, class_listers: Union[str, List[str]] = None, env_class_listers: str = None,
                 excluded_class_listers: Union[str, List[str]] = None, env_excluded_class_listers: str = None):

        self._classes = dict()
        self._class_listers = None
        self._env_class_listers = None
        self._excluded_class_listers = None
        self._env_excluded_class_listers = None

        self.class_listers = class_listers
        self.env_class_listers = env_class_listers
        self.excluded_class_listers = excluded_class_listers
        self.env_excluded_class_listers = env_excluded_class_listers

    @property
    def class_listers(self) -> Optional[List[str]]:
        """
        Returns the class lister functions.

        :return: the functions
        :rtype: list
        """
        return self._class_listers

    @class_listers.setter
    def class_listers(self, class_listers: Optional[Union[str, List[str]]]):
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
            raise Exception("class_listers must be either str or list, but got: %s" % str(type(class_listers)))
        self._class_listers = class_listers
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
            att = getattr(module, att_name)
            if inspect.isclass(att) and not inspect.isabstract(att) and not isinstance(att, abc.ABCMeta) and issubclass(att, cls):
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
                if self.excluded_class_listers is not None:
                    if class_lister in self.excluded_class_listers:
                        continue

                module_name, func_name = class_lister.split(":")
                try:
                    module = importlib.import_module(module_name)
                except:
                    print("Failed to import class lister module: %s" % module_name, file=sys.stderr)
                    traceback.print_exc()
                    continue

                if hasattr(module, func_name):
                    func = getattr(module, func_name)
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

        # from environment
        if self.env_class_listers is not None:
            env_classes = self._determine_from_env(c)
            if env_classes is not None:
                all_classes.update(env_classes)

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
