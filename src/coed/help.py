import abc
from coed.config import AbstractOptionHandler


class AbstractHelpGenerator(AbstractOptionHandler, abc.ABC):
    """
    Ancestor for classes that generate help from option handlers.
    """

    def file_extension(self) -> str:
        """
        Returns the preferred file extension.

        :return: the file extension (incl dot)
        :rtype: str
        """
        raise NotImplementedError()

    def _do_generate(self, handler: AbstractOptionHandler) -> str:
        """
        Performs the actual generation.

        :param handler: the option handler to generate the help for
        :type handler: AbstractOptionHandler
        :return: the generate string
        :rtype: str
        """
        raise NotImplementedError()

    def generate(self, handler: AbstractOptionHandler, output_path: str = None):
        """
        Generates help for the supplied option handler.

        :param handler: the option handler to generate the help for
        :type handler: AbstractOptionHandler
        :param output_path: the file to store the help in, uses stdout if not provided
        :type output_path: str
        """

        help = self._do_generate(handler)
        if output_path is None:
            print(help)
        else:
            with open(output_path, "w") as hf:
                hf.write(help)
