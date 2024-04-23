import traceback
from datetime import datetime


def log(*args):
    """
    Just outputs the arguments with a timestamp.

    :param args: the arguments to log
    """
    print(*("%s - " % str(datetime.now()), *args))


def handle_exception(msg: str, loggable: 'LoggableObject' = None) -> str:
    """
    Generates a string from message and the current exception.

    :param msg: the message to use
    :type msg: str
    :param loggable: the LoggableObject instance
    :return: the generated string
    :rtype: str
    """
    result = msg + "\n" + traceback.format_exc()
    if loggable is not None:
        loggable.log(result)
    return result


class LoggableObject(object):
    """
    Ancestor for objects that can output logging information.
    """

    def log(self, *args):
        """
        Logs the arguments.

        :param args: the arguments to log
        """
        print(*("%s - %s -" % (type(self).__name__, str(datetime.now())), *args))

    def _handle_exception(self, msg: str) -> str:
        """
        Generates a string from message and the current exception.

        :param msg: the message to use
        :type msg: str
        :return: the generated string
        :rtype: str
        """
        return handle_exception(msg, loggable=self)
