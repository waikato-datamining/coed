from typing import Dict, Optional

DICT_READERS = None
""" contains all dictionary readers (class -> reader) """

DICT_WRITERS = None
""" contains all dictionary writers (class -> writer) """


def get_dict_readers() -> Dict:
    """
    Returns the registered readers.

    :return: the readers
    :rtype: dict
    """
    global DICT_READERS
    if DICT_READERS is None:
        DICT_READERS = dict()
    return DICT_READERS


def add_dict_reader(cls, reader):
    """
    Adds a reader for the specified class.

    :param cls: the class to add the reader for
    :type cls: object
    :param reader: the reader method to add
    :type reader: object
    """
    get_dict_readers()[cls] = reader


def has_dict_reader(cls) -> bool:
    """
    Checks whether a reader is registered for the class.

    :param cls: the class to check
    :type cls: object
    :return: true if reader registered
    :rtype: bool
    """
    return cls in get_dict_readers()


def get_dict_reader(cls) -> Optional:
    """
    Returns the reader registered for the class.

    :param cls: the class to get the reader for
    :type cls: object
    :return: the reader method, None if none registered
    :rtype: object
    """
    if has_dict_reader(cls):
        return get_dict_readers()[cls]
    else:
        return None


def get_dict_writers() -> Dict:
    """
    Returns the registered writers.

    :return: the writers
    :rtype: dict
    """
    global DICT_WRITERS
    if DICT_WRITERS is None:
        DICT_WRITERS = dict()
    return DICT_WRITERS


def add_dict_writer(cls, writer):
    """
    Adds a writer for the specified class.

    :param cls: the class to add the writer for
    :type cls: object
    :param writer: the writer method to add
    :type writer: object
    """
    get_dict_writers()[cls] = writer


def has_dict_writer(cls) -> bool:
    """
    Checks whether a writer is registered for the class.

    :param cls: the class to check
    :type cls: object
    :return: true if writer registered
    :rtype: bool
    """
    return cls in get_dict_writers()


def get_dict_writer(cls) -> Optional:
    """
    Returns the writer registered for the class.

    :param cls: the class to get the writer for
    :type cls: object
    :return: the writer method, None if none registered
    :rtype: object
    """
    if has_dict_writer(cls):
        return get_dict_writers()[cls]
    else:
        return None
