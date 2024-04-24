import abc
import json
from collections import OrderedDict
from datetime import datetime
from typing import List, Union, Optional, Any, Dict
from coed.class_utils import class_name_to_type, get_class_name
from coed.logging import LoggableObject
from coed.serialization.objects import get_dict_reader, get_dict_writer, add_dict_writer, add_dict_reader, has_dict_reader, has_dict_writer
from coed.serialization.vars import get_string_reader
from coed.vars import is_valid_name, is_var, pad_var, unpad_var, VariableHandler, Variables
from coed.serialization.vars import AbstractStringReader, AbstractStringWriter
import coed.serialization.vars as ser_vars


class Option:
    """
    Defines a single option.
    """

    def __init__(self, name: str, value_type, def_value, help: str, base_type=None,
                 lower: Union[int, float] = None, upper: Union[int, float] = None,
                 choices: Optional[List] = None):
        """
        Initializes the item.

        :param name: the name of the item
        :type name: str
        :param value_type: the class of the value
        :type value_type: object
        :param def_value: the default value
        :type def_value: object
        :param help: the help string
        :type help: str
        :param base_type: the base class of the value, in case of lists
        :type base_type: object
        :param lower: the lower bound (for numbers, incl), unbounded if None
        :param lower: int or float
        :param upper: the upper bound (for numbers, incl), unbounded if None
        :param upper: int or float
        :param choices: the list of available options to choose from
        :type choices: list
        """
        if name == "class":
            raise Exception("Cannot use reserved name: %s" % name)
        self.name = name
        self.value_type = value_type
        self.def_value = def_value
        self.help = help
        self.base_type = base_type
        self.var = None
        self.lower = lower
        self.upper = upper
        self.choices = choices

    def is_in_range(self, value) -> Optional[str]:
        """
        If lower or upper numeric bound defined, checks whether the value is within range.
        If choices are defined, checks whether the value is a valid choice.

        :param value: the numeric value to check against the bounds or element to check against stored choices
        :return: None if within range, otherwise error message
        :rtype: str
        """
        if self.lower is not None:
            if value < self.lower:
                return "Below lower bound: %s < %s" % (str(value), str(self.lower))
        if self.upper is not None:
            if value > self.upper:
                return "Above upper bound: %s > %s" % (str(value), str(self.upper))
        if self.choices is not None:
            if value not in self.choices:
                return "%s is not a valid choice, available: %s" % (str(value), str(self.choices))
        return None

    def __str__(self) -> str:
        """
        Returns a string describing the item.

        :return: the string describing the item
        :rtype: str
        """
        return "%s/%s: %s\n   %s" % (self.name, str(self.value_type.__name__), repr(self.def_value), self.help)


class OptionManager(LoggableObject, VariableHandler):
    """
    Manages multiple options.
    """

    def __init__(self):
        """
        Initializes the manager.
        """
        self._options = OrderedDict()
        self._values = dict()
        self._to_dict_handlers = dict()
        self._from_dict_handlers = dict()
        self._variables = Variables()

    @property
    def variables(self) -> Variables:
        """
        Returns the variables.

        :return: the variables object
        :rtype: Variables
        """
        return self._variables

    def update_variables(self, variables: Variables):
        """
        Sets the variables to use.

        :param variables: the variables to use
        :type variables: Variables
        """
        self._variables = variables
        for k in self._options:
            if isinstance(self._options[k].def_value, VariableHandler):
                self._options[k].def_value.update_variables(variables)
                if k in self._values:
                    self._values[k].update_variables(variables)
            if (issubclass(self._options[k].value_type, list)) and (self._options[k].base_type is not None):
                if issubclass(self._options[k].base_type, VariableHandler):
                    for i in range(len(self._options[k].def_value)):
                        self._options[k].def_value[i].update_variables(variables)
                    if k in self._values:
                        for i in range(len(self._values[k])):
                            self._values[k][i].update_variables(variables)

    def has_var(self, name: str) -> bool:
        """
        Returns whether the specified option has a variable attached.

        :param name: the name of the option to look for
        :type name: str
        :return: true if the option has a variable
        :rtype: bool
        """
        return self.has(name) and (self._options[name].var is not None)

    def set_var(self, name: str, var: str):
        """
        Attaches the variable to the specified option.

        :param name: the name of the item to update its value for
        :type name: str
        :param var: the new value
        :type var: str
        """
        if not self.has(name):
            raise Exception("Unknown option: %s" % name)
        if not is_valid_name(var):
            raise Exception("Invalid variable name: %s" % var)
        self._options[name].var = var

    def get_var(self, name: str) -> str:
        """
        Returns the variable attached to the specified option.

        :param name: the name of the option to get the variable for
        :type name: str
        :return: the attached variable, None if none attached
        :rtype: str
        """
        if not self.has(name):
            raise Exception("Unknown option: %s" % name)
        return self._options[name].var

    def remove_var(self, name: str):
        """
        Removes the variable attached to the specified option.

        :param name: the name of option to update
        :type name: str
        """
        if not self.has(name):
            raise Exception("Unknown option: %s" % name)
        self._options[name].var = None

    def detect_vars(self, skip: Optional[List[str]] = None) -> List[str]:
        """
        Detects the variables that are attached to its options.

        :param skip: the list of classes to skip
        :type skip: list
        :return: the list of detected variable names (unpadded)
        :rtype: list
        """
        result = []
        for k in self._options:
            option = self._options[k]
            if skip is not None:
                if (option.value_type in skip) or (option.base_type in skip):
                    continue
            if option.var is not None:
                result.append(option.var)
            # recurse
            if k in self._values:
                if issubclass(option.value_type, AbstractOptionHandler):
                    result.extend(self._values[k].option_manager.detect_vars(skip=skip))
                if (option.base_type is not None) and issubclass(option.base_type, AbstractOptionHandler):
                    for l in self._values[k]:
                        result.extend(l.option_manager.detect_vars(skip=skip))
        return result

    def options(self) -> List[Option]:
        """
        Returns all options.

        :return: the options
        :rtype: list
        """
        return list(self._options.values())

    def add(self, option: Option) -> 'OptionManager':
        """
        Adds the option.

        :param option: the item to add
        :type option: Option
        :return: itself
        :rtype: OptionManager
        """
        self._options[option.name] = option
        return self

    def has(self, name: str) -> bool:
        """
        Returns whether the specified option is specified.

        :param name: the name of the item to look for
        :type name: str
        :return: true if the item is present
        :rtype: bool
        """
        return name in self._options

    def set(self, name: str, value) -> 'OptionManager':
        """
        Sets the config value.

        :param name: the name of the item to update its value for
        :type name: str
        :param value: the new value
        :return: itself
        :rtype: OptionManager
        """
        if not self.has(name):
            raise Exception("Invalid option name: %s" % name)
        opt = self._options[name]
        if is_var(value):
            opt.var = unpad_var(value)
        else:
            if not isinstance(value, opt.value_type):
                raise Exception("Invalid config type for %s: expected=%s, received=%s" % (name, str(opt.value_type), str(type(value))))
            msg = opt.is_in_range(value)
            if msg is not None:
                raise Exception("Invalid value for %s: %s" % (name, msg))
            self._values[name] = value
        return self

    def get(self, name: str) -> Any:
        """
        Returns the currently stored value or the default value.

        :param name: the name of the value to retrieve
        :type name: str
        :return: the value, None if invalid option name
        :rtype: object
        """
        if not self.has(name):
            return None
        # variable attached? return associated value
        if self.has_var(name) and (self.variables.has(self.get_var(name))):
            value = self.variables.get(self.get_var(name))
            reader = get_string_reader(self._options[name].value_type)
            if (reader is None) and (self._options[name].base_type is not None):
                reader = get_string_reader(self._options[name].base_type)
            if reader is not None:
                return reader().convert(value, base_type=self._options[name].base_type)
            else:
                self.log("Failed to determine reader for %s" % name)
        # non-default value set?
        if name in self._values:
            return self._values[name]
        # default value
        return self._options[name].def_value

    def reset(self):
        """
        Resets all options to default values.
        """
        self._values.clear()

    def set_to_dict_handler(self, name: str, handler: Any):
        """
        Sets the read method that handles the specified option.

        :param name: the name of the option to handle
        :type name: str
        :param handler: the handler function
        """
        self._to_dict_handlers[name] = handler

    def has_to_dict_handler(self, name: str) -> bool:
        """
        Checks whether a read handler is set for the option.

        :param name: the name of the option
        :type name: str
        :return: true if a handler method registered
        :rtype: bool
        """
        return name in self._to_dict_handlers

    def get_to_dict_handler(self, name: str) -> Any:
        """
        Returns the handler registered for the option.

        :param name: the name of the option
        :type name: str
        :return: the handler, None if no handler registered
        """
        if not self.has_to_dict_handler(name):
            return None
        else:
            return self._to_dict_handlers[name]

    def set_from_dict_handler(self, name: str, handler: Any):
        """
        Sets the write method that handles the specified option.

        :param name: the name of the option to handle
        :type name: str
        :param handler: the handler function
        """
        self._from_dict_handlers[name] = handler

    def has_from_dict_handler(self, name: str) -> bool:
        """
        Checks whether a write handler is set for the option.

        :param name: the name of the option
        :type name: str
        :return: true if a handler method registered
        :rtype: bool
        """
        return name in self._from_dict_handlers

    def get_from_dict_handler(self, name: str) -> Any:
        """
        Returns the handler registered for the option.

        :param name: the name of the option
        :type name: str
        :return: the handler, None if no handler registered
        """
        if not self.has_from_dict_handler(name):
            return None
        else:
            return self._from_dict_handlers[name]

    def from_dict(self, d: Dict):
        """
        Sets all the values from the dictionary.

        :param d: the dictionary to get the values from
        :type d: dict
        """
        for k in d:
            if k not in self._options:
                self.log("Unknown option: %s/%s" % (k, d[k]))
                continue

            # variable?
            if isinstance(d[k], str) and is_var(d[k]):
                self._options[k].var = unpad_var(d[k])
                continue

            # was a base type define for the elements of the list?
            if isinstance(d[k], list) and (self._options[k].base_type is not None):
                if has_dict_reader(self._options[k].base_type):
                    reader = get_dict_reader(self._options[k].base_type)
                    l = []
                    for item in d[k]:
                        # already object rather than dict?
                        if isinstance(item, self._options[k].base_type):
                            l.append(item)
                        else:
                            l.append(reader(item))
                    self.set(k, l)
                    continue
                else:
                    l = []
                    for item in d[k]:
                        if (type(item) == str) and (self._options[k].base_type is not str):
                            item = self._options[k].base_type(item)
                        l.append(item)
                    self.set(k, l)
                    continue

            # special handler registered?
            if self.has_from_dict_handler(k):
                handler = self.get_from_dict_handler(k)
                self.set(k, handler(d[k]))
                continue

            # reader registered for type?
            if has_dict_reader(self._options[k].value_type):
                # already object rather than dict?
                if isinstance(d[k], self._options[k].value_type):
                    self.set(k, d[k])
                else:
                    reader = get_dict_reader(self._options[k].value_type)
                    self.set(k, reader(d[k]))
                continue

            # str derived class but str value? lets wrap it in correct class
            if (type(d[k]) == str) and (self._options[k].value_type is not str):
                d[k] = self._options[k].value_type(d[k])

            if isinstance(self.get(k), self._options[k].value_type):
                self.set(k, d[k])
            else:
                self.log("Incorrect type: %s/%s/%s" % (k, str(d[k]), str(type(d[k]))))

    def to_dict(self, skip_default: bool = False) -> Dict:
        """
        Returns all the options as dictionary.

        :param skip_default: if enabled, skips values that are default ones
        :type skip_default: bool
        :return: the options as dictionary
        :rtype: dict
        """
        result = dict()
        for k in self._options:
            # variable attached?
            if self.has_var(k):
                result[k] = pad_var(self.get_var(k))
                continue

            if isinstance(self.get(k), list) and (self._options[k].base_type is not None):
                if has_dict_writer(self._options[k].base_type):
                    writer = get_dict_writer(self._options[k].base_type)
                    l = []
                    for item in self.get(k):
                        l.append(writer(item))
                    result[k] = l
                    continue

            # special handler registered?
            if self.has_to_dict_handler(k):
                handler = self.get_to_dict_handler(k)
                result[k] = handler(self.get(k))
                continue

            # writer registered for type?
            if has_dict_writer(self._options[k].value_type):
                writer = get_dict_writer(self._options[k].value_type)
                result[k] = writer(self.get(k))
                continue

            if not skip_default or (self.get(k) != self._options[k].def_value):
                result[k] = self.get(k)
        return result


class AbstractOptionHandler(LoggableObject, VariableHandler, abc.ABC):
    """
    The ancestor for all classes that handle options.
    """

    def __init__(self, options: Dict = None):
        """
        Initializes the object.

        :param options: the options to set immediately
        :type options: dict
        """
        self._initialize()
        self._define_options()
        self.reset()
        if options is not None:
            self.options = options

    def _initialize(self):
        """
        Performs initializations.
        """
        self._log_prefix = type(self).__name__

    def _define_options(self):
        """
        For configuring the options.
        """
        self._option_manager = OptionManager()
        self._option_manager.add(Option("debug", bool, False, "If enabled, outputs some debugging information"))

    def reset(self):
        """
        Resets the state of the object.
        """
        pass

    def description(self) -> str:
        """
        Returns a description for the object.

        :return: the object description
        :rtype: str
        """
        return "-description missing-"

    @property
    def option_manager(self) -> OptionManager:
        """
        Returns the option manager.

        :return: the manager
        :rtype: OptionManager
        """
        return self._option_manager

    @property
    def options(self) -> Dict:
        """
        Returns the current options.

        :return: the current options
        :rtype: dict
        """
        return self._option_manager.to_dict(skip_default=True)

    @options.setter
    def options(self, d: Dict):
        """
        Sets the options to use.

        :param d: the options to set
        :type d: dict
        """
        if d is None:
            d = dict()
        self._option_manager.from_dict(d)
        self.reset()

    @property
    def is_debug(self) -> bool:
        """
        Returns whether debug mode is on.

        :return: true if on
        :rtype: bool
        """
        return self.get("debug")

    def get(self, name: str) -> Any:
        """
        Returns the value for the specified option.

        :param name: the name of the option to retrieve
        :type name: str
        :return: the value of the option, None if invalid option
        """
        return self._option_manager.get(name)

    def set(self, name: str, value: Any) -> 'AbstractOptionHandler':
        """
        Sets the value for the specified option.

        :param name: the name of the option to set
        :type name: str
        :param value: the value of the option to set
        :type value: object
        :return: itself
        :rtype: AbstractOptionHandler
        """
        self._option_manager.set(name, value)
        return self

    @property
    def variables(self) -> Variables:
        """
        Returns the variables.

        :return: the variables object
        :rtype: Variables
        """
        return self.option_manager.variables

    def update_variables(self, variables: Variables):
        """
        Sets the variables to use.

        :param variables: the variables to use
        :type variables: Variables
        """
        return self.option_manager.update_variables(variables)

    def _get_log_prefix(self) -> str:
        """
        Returns the log prefix for this object.

        :return: the prefix
        :rtype: str
        """
        return self._log_prefix

    @property
    def log_prefix(self) -> str:
        """
        Returns the log prefix for this object.

        :return: the prefix
        :rtype: str
        """
        return self._get_log_prefix()

    def log(self, *args):
        """
        Logs the arguments.

        :param args: the arguments to log
        """
        print(*("%s - %s -" % (self.log_prefix, str(datetime.now())), *args))


def dict_to_optionhandler(d: Dict) -> AbstractOptionHandler:
    """
    Turns the dictionary into an option handler.

    :param d: the dictionary describing the actor
    :type d: dict
    :return: the option handler
    :rtype: AbstractOptionHandler
    """
    result = class_name_to_type(d["class"])()
    if "options" in d:
        result.options = d["options"]
    else:
        result.options = dict()
    return result


def optionhandler_to_dict(a: Any) -> Dict:
    """
    Turns the option handler into a dictionary describing it.

    :param a: the option handler to convert
    :type a: AbstractOptionHandler
    :return: the generated dictionary
    :rtype: dict
    """
    result = dict()
    result["class"] = get_class_name(a)
    options = a.options
    if len(options) != 0:
        result["options"] = a.options
    return result


# register reader/writer
add_dict_writer(AbstractOptionHandler, optionhandler_to_dict)
add_dict_reader(AbstractOptionHandler, dict_to_optionhandler)


class OptionHandlerStringReader(AbstractStringReader):
    """
    Instantiates option handlers from strings.
    """

    def handles(self, cls):
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, AbstractOptionHandler)

    def convert(self, s: str, base_type=None):
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        d = json.loads(s)
        return dict_to_optionhandler(d)


class OptionHandlerStringWriter(AbstractStringWriter):
    """
    Turns option handlers into strings.
    """

    def handles(self, cls):
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, AbstractOptionHandler)

    def convert(self, o) -> str:
        """
        Turns the object into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        d = optionhandler_to_dict(o)
        return json.dumps(d)


# add default readers
ser_vars.add_string_reader(OptionHandlerStringReader)

# add default writers
ser_vars.add_string_writer(OptionHandlerStringWriter)
