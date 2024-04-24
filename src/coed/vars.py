from typing import Tuple, Any, Set
from coed.serialization.vars import AbstractStringReader, add_string_reader


VARIABLE_EVENT_ADDED = "added"
VARIABLE_EVENT_UPDATED = "updated"
VARIABLE_EVENT_DELETED = "deleted"
VARIABLE_EVENT_CLEARED = "cleared"

VARIABLE_EVENTS = [
    VARIABLE_EVENT_ADDED,
    VARIABLE_EVENT_UPDATED,
    VARIABLE_EVENT_DELETED,
    VARIABLE_EVENT_CLEARED,
]

VALID_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"

VAR_START = "@{"

VAR_END = "}"


def is_valid_name(s: str) -> bool:
    """
    Checks whether the string is a valid variable name.

    :param s: the string to check
    :type s: str
    :return: True if valid
    :rtype: bool
    """
    for i in range(len(s)):
        if s[i] not in VALID_CHARS:
            return False
    return True


def is_var(s: str) -> bool:
    """
    Checks whether the string is a (padded) variable name.

    :param s: the string to check
    :type s: str
    :return: True if a padded variable name
    :rtype: bool
    """
    return isinstance(s, str) and s.startswith(VAR_START) and s.endswith(VAR_END)


def pad_var(s: str) -> str:
    """
    Pads the variable name.

    :param s: the variable name to pad
    :type s: str
    :return: the padded name
    :rtype: str
    """
    return VAR_START + s + VAR_END


def unpad_var(s: str) -> str:
    """
    Removes the padding of the variable name.

    :param s: the variable name to unpad
    :type s: str
    :return: the unpadded name
    :rtype: str
    """
    if is_var(s):
        return s[len(VAR_START):len(s) - len(VAR_END)]
    else:
        return s


def _do_expand(s: str, variables: 'Variables') -> Tuple[str, bool]:
    """
    Expands the variable placeholders in the string using the supplied variables.

    :param s: the string to expand
    :type s: str
    :param variables: the variables to use for the expansion
    :type variables: Variables
    :return: the expanded string and whether anything was expanded
    :rtype: tuple(str, bool)
    """
    result = ""
    expanded = False

    tmp = s
    while (VAR_START in tmp) and (VAR_END in tmp):
        start = tmp.find(VAR_START)
        end = tmp.find(VAR_END, start)
        if (start == -1) or (end == -1):
            print("Failed to fully expand: " + s)
            break
        else:
            name = tmp[start+len(VAR_START):end]
            result += tmp[0:start]
            if variables.has(name):
                result += str(variables.get(name))
            if len(tmp) == end + 1:
                tmp = ""
            else:
                tmp = tmp[end+1:]
            expanded = True

    if len(tmp) > 0:
        result += tmp

    return result, expanded


def expand(s: str, variables: 'Variables') -> str:
    """
    Expands the variable placeholders in the string using the supplied variables.

    :param s: the string to expand
    :type s: str
    :param variables: the variables to use for the expansion
    :type variables: Variables
    :return: the expanded string
    :rtype: str
    """
    result = s
    while True:
        result, expanded = _do_expand(result, variables)
        if not expanded:
            break
        if VAR_START not in result:
            break

    return result


class VariableChangeEvent:
    """
    Event that gets sent out if variables change.
    """

    def __init__(self, variables: 'Variables', event_type: str, var: str = None):
        """
        Initializes the event.

        :param variables: the affected variables object
        :type variables: Variables
        :param event_type: the event type
        :type event_type: str
        :param var: the affected variable name (unpadded)
        :type var: str
        """
        if (event_type is not None) and (event_type not in VARIABLE_EVENTS):
            raise Exception("Invalid variable event type: %s" % event_type)
        self.variables = variables
        self.event_type = event_type
        self.var = var


class VariableName(str):
    """
    Class that enforces correct variable names.
    """

    def __new__(cls, s):
        if not is_valid_name(s):
            raise Exception("Invalid variable name: %s" % s)
        return super().__new__(cls, s)


class VariableNameStringReader(AbstractStringReader):
    """
    Turns strings into VariableName objects.
    """

    def handles(self, cls):
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, VariableName)

    def convert(self, s: str, base_type: Any = None) -> Any:
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return VariableName(s)


class VariableChangeListener:
    """
    Interface for classes that listen to variable change events.
    """

    def variables_changed(self, event: VariableChangeEvent):
        """
        Gets called when the variable changes.

        :param event: the event
        :type event: VariableChangeEvent
        """
        raise NotImplementedError()


class Variables:
    """
    Manages the variables.
    """

    def __init__(self):
        """
        Initializes the variables.
        """
        self._data = dict()
        self._listeners = set()

    def add_listener(self, l: VariableChangeListener):
        """
        Adds the listener for events.

        :param l: the listener to add
        :type l: VariableChangeListener
        :return: itself
        :rtype: Variables
        """
        self._listeners.add(l)
        return self

    def remove_listener(self, l: VariableChangeListener) -> 'Variables':
        """
        Removes the specified listener.

        :param l: the listener to remove
        :type l: VariableChangeListener
        :return: itself
        :rtype: Variables
        """
        if l in self._listeners:
            self._listeners.remove(l)
        return self

    def clear_listeners(self) -> 'Variables':
        """
        Removes all listeners.

        :return: itself
        :rtype: Variables
        """
        self._listeners.clear()
        return self

    def clear(self) -> 'Variables':
        """
        Removes all stored items.

        :return: itself
        :rtype: Variables
        """
        self._data.clear()
        self._notify_listeners(VariableChangeEvent(self, VARIABLE_EVENT_CLEARED))
        return self

    def has(self, key: str) -> bool:
        """
        Checks whether a variable item is available for the name.

        :param key: the variable name to look up
        :type key: str
        :return: True if available
        :rtype: bool
        """
        if not is_valid_name(key):
            raise Exception("Invalid variable name: %s" + key)
        return key in self._data

    def set(self, key: str, value: Any) -> 'Variables':
        """
        Sets the specified variable.

        :param key: the key for the item
        :type key: str
        :param value: the value to store
        :type value: object
        :return: itself
        :rtype: Variables
        """
        if not is_valid_name(key):
            raise Exception("Invalid variable name: %s" + key)
        if key not in self._data:
            self._data[key] = value
            self._notify_listeners(VariableChangeEvent(self, VARIABLE_EVENT_ADDED, key))
        else:
            self._data[key] = value
            self._notify_listeners(VariableChangeEvent(self, VARIABLE_EVENT_UPDATED, key))
        return self

    def get(self, key: str) -> Any:
        """
        Returns the variable value.

        :param key: the key to get the value for
        :type key: str
        :return: the variable value, None if not available
        :rtype: object
        """
        if not is_valid_name(key):
            raise Exception("Invalid variable name: %s" + key)
        if key in self._data:
            return self._data[key]
        else:
            return None

    def remove(self, key: str) -> 'Variables':
        """
        Removes the variable value.

        :param key: the name of the value to remove
        :type key: str
        :return: itself
        :rtype: Variables
        """
        if not is_valid_name(key):
            raise Exception("Invalid variable name: %s" + key)
        if key in self._data:
            del self._data[key]
            self._notify_listeners(VariableChangeEvent(self, VARIABLE_EVENT_DELETED, key))
        return self

    def keys(self) -> Set:
        """
        Returns all the names of the currently stored variables.

        :return: the set of names
        :rtype: set
        """
        return set(self._data.keys())

    def expand(self, s: str) -> str:
        """
        Expands any variables in the string.

        :param s: the string to expand
        :type s: str
        :return: the expanded string
        :rtype: str
        """
        return expand(s, self)

    def merge(self, variables: 'Variables') -> 'Variables':
        """
        Incorporates the supplied variables (replaces any existing ones).

        :param variables: the variables to merge
        :type variables: Variables
        :return: itself
        :rtype: Variables
        """
        for key in variables.keys():
            self.set(key, variables.get(key))
        return self

    def _notify_listeners(self, event: VariableChangeEvent):
        """
        Notifies all listeners with the event.

        :param event: the event to send
        :type event: VariableChangeEvent
        """
        for l in self._listeners:
            l.variables_changed(event)

    def __str__(self) -> str:
        """
        Returns a string representation of the stored variables.

        :return: the stored variables
        :rtype: str
        """
        return str(self._data)


class VariableHandler:
    """
    Interface for classes that manage variables.
    """

    @property
    def variables(self) -> Variables:
        """
        Returns the variables.

        :return: the variables
        :rtype: Variables
        """
        raise NotImplementedError()

    def update_variables(self, variables: Variables):
        """
        Sets the variables to use.

        :param variables: the variables to use
        :type variables: Variables
        """
        raise NotImplementedError()


# serialization
add_string_reader(VariableNameStringReader)
