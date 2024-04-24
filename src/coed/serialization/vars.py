import abc
from typing import Any, Type, Optional, Dict, List
import json


STRING_READERS = None
""" contains all readers that convert strings into objects (list of AbstractStringReader) """

STRING_WRITERS = None
""" contains all writers that convert objects into strings (list of AbstractStringWriter) """

STRING_READERS_CACHE = None
""" cache of class to AbstractStringReader relation """

STRING_WRITERS_CACHE = None
""" cache of class to AbstractStringWriter relation """


class AbstractStringReader(abc.ABC):
    """
    Ancestor for classes that turn strings into objects.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        raise NotImplementedError()

    def convert(self, s: str, base_type: Type = None):
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        raise NotImplementedError()


class StringReader(AbstractStringReader):
    """
    Ancestor for classes that turn strings into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, str)

    def convert(self, s: str, base_type: Type = None) -> Any:
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return str(s)


class BoolStringReader(AbstractStringReader):
    """
    Ancestor for classes that turn strings into bool.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, bool)

    def convert(self, s: str, base_type: Type = None) -> Any:
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return bool(s)


class IntStringReader(AbstractStringReader):
    """
    Ancestor for classes that turn strings into int.
    """

    def handles(self, cls: type) -> bool:
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, int)

    def convert(self, s: str, base_type: Type = None) -> Any:
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return int(s)


class FloatStringReader(AbstractStringReader):
    """
    Ancestor for classes that turn strings into float.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, float)

    def convert(self, s: str, base_type: Type = None) -> Any:
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return float(s)


class ListStringReader(AbstractStringReader):
    """
    Ancestor for classes that turns list strings into lists.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, list)

    def convert(self, s: str, base_type: Type = None) -> Any:
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        result = list()
        l = json.loads(s)
        reader = None
        if base_type is not None:
            reader = get_string_reader(base_type)()
        for item in l:
            if reader is None:
                result.append(item)
            else:
                result.append(reader.convert(item, base_type))
        return result


class AbstractStringWriter(abc.ABC):
    """
    Ancestor for classes that turn objects into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        raise NotImplementedError()

    def convert(self, o: Any) -> str:
        """
        Turns the object into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        raise NotImplementedError()


class StringWriter(AbstractStringWriter):
    """
    Ancestor for classes that turn strings into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, str)

    def convert(self, o: Any) -> str:
        """
        Turns the object into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        return str(o)


class BoolStringWriter(AbstractStringWriter):
    """
    Ancestor for classes that turn bools into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, bool)

    def convert(self, o: Any) -> str:
        """
        Turns the object into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        return str(o)


class IntStringWriter(AbstractStringWriter):
    """
    Ancestor for classes that turn objects into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, int)

    def convert(self, o: Any) -> str:
        """
        Turns the object into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        return str(o)


class FloatStringWriter(AbstractStringWriter):
    """
    Ancestor for classes that turn objects into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, float)

    def convert(self, o: Any) -> str:
        """
        Turns the object into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        return str(o)


class ListStringWriter(AbstractStringWriter):
    """
    Ancestor for classes that turn lists into strings.
    """

    def handles(self, cls: Any) -> bool:
        """
        Whether it can convert the object into a string.

        :param cls: the class to convert
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, list)

    def convert(self, o: Any) -> str:
        """
        Turns the list into a string.

        :param o: the object to convert
        :return: the generated string
        :rtype: str
        """
        l = list()
        for item in o:
            writer = get_string_writer(type(item))
            if writer is None:
                l.append(str(item))
            else:
                l.append(writer.convert(item))
        return json.dumps(l)


def get_string_readers() -> List:
    """
    Returns the registered readers.

    :return: the readers
    :rtype: list
    """
    global STRING_READERS
    if STRING_READERS is None:
        STRING_READERS = list()
    return STRING_READERS


def get_string_readers_cache() -> Dict:
    """
    Returns the cache for registered readers (class -> reader).

    :return: the readers
    :rtype: dict
    """
    global STRING_READERS_CACHE
    if STRING_READERS_CACHE is None:
        STRING_READERS_CACHE = dict()
    return STRING_READERS_CACHE


def add_string_reader(reader: Type):
    """
    Adds a reader.

    :param reader: the reader to add
    :type reader: object
    """
    get_string_readers().append(reader)


def has_string_reader(cls) -> bool:
    """
    Checks whether a reader is registered for the class.

    :param cls: the class to check
    :type cls: object
    :return: true if reader registered
    :rtype: bool
    """
    return get_string_reader(cls) is not None


def get_string_reader(cls) -> Optional:
    """
    Returns the reader registered for the class.

    :param cls: the class to get the reader for
    :type cls: object
    :return: the reader method, None if none registered
    """
    if cls in get_string_readers_cache():
        if isinstance(get_string_readers_cache()[cls], bool):
            # we store False as a placeholder
            return None
        else:
            return get_string_readers_cache()[cls]

    # iterate readers to see whether any can handle the class
    for reader in get_string_readers():
        if issubclass(reader, StringReader):
            continue
        if reader().handles(cls):
            get_string_readers_cache()[cls] = reader
            return reader
    if StringReader().handles(cls):
        get_string_readers_cache()[cls] = StringReader
        return StringReader

    # flag entry
    get_string_readers_cache()[cls] = False
    return None


def get_string_writers() -> List:
    """
    Returns the registered writers.

    :return: the writers
    :rtype: list
    """
    global STRING_WRITERS
    if STRING_WRITERS is None:
        STRING_WRITERS = list()
    return STRING_WRITERS


def get_string_writers_cache() -> Dict:
    """
    Returns the cache for registered writers (class -> writer).

    :return: the writers
    :rtype: dict
    """
    global STRING_WRITERS_CACHE
    if STRING_WRITERS_CACHE is None:
        STRING_WRITERS_CACHE = dict()
    return STRING_WRITERS_CACHE


def add_string_writer(writer: Type):
    """
    Adds a writer for the specified class.

    :param writer: the writer method to add
    :type writer: object
    """
    get_string_writers().append(writer)


def has_string_writer(cls) -> bool:
    """
    Checks whether a writer is registered for the class.

    :param cls: the class to check
    :type cls: object
    :return: true if writer registered
    :rtype: bool
    """
    return get_string_writer(cls) is not None


def get_string_writer(cls) -> Optional:
    """
    Returns the writer registered for the class.

    :param cls: the class to get the writer for
    :type cls: object
    :return: the writer method, None if none registered
    :rtype: object
    """
    if cls in get_string_writers_cache():
        if isinstance(get_string_writers_cache()[cls], bool):
            # we store False as a placeholder
            return None
        else:
            return get_string_writers_cache()[cls]

    # iterate writers to see whether any can handle the class
    for writer in get_string_writers():
        if issubclass(writer, StringWriter):
            continue
        if writer().handles(cls):
            get_string_writers_cache()[cls] = writer
            return writer
    if StringWriter().handles(cls):
        get_string_writers_cache()[cls] = StringWriter
        return StringWriter

    # flag entry
    get_string_writers_cache()[cls] = False
    return None


# add default readers
add_string_reader(StringReader)
add_string_reader(BoolStringReader)
add_string_reader(IntStringReader)
add_string_reader(FloatStringReader)
add_string_reader(ListStringReader)

# add default writers
add_string_writer(StringWriter)
add_string_writer(BoolStringWriter)
add_string_writer(IntStringWriter)
add_string_writer(FloatStringWriter)
add_string_writer(ListStringWriter)
