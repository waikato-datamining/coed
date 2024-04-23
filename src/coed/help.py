from typing import Any, Tuple, List
from coed.config import AbstractOptionHandler
from coed.class_utils import find_classes, get_class_name


class AbstractHelpGenerator(AbstractOptionHandler):
    """
    Ancestor for classes that generate help from option handlers.
    """

    def file_extension(self) -> str:
        """
        Returns the preferred file extension.

        :return: the file extension (incl dot)
        :rtype: str
        """
        raise NotImplemented()

    def _do_generate(self, handler: AbstractOptionHandler) -> str:
        """
        Performs the actual generation.

        :param handler: the option handler to generate the help for
        :type handler: AbstractOptionHandler
        :return: the generate string
        :rtype: str
        """
        raise NotImplemented()

    def generate(self, handler: AbstractOptionHandler, fname: str = None):
        """
        Generates help for the supplied option handler.

        :param handler: the option handler to generate the help for
        :type handler: AbstractOptionHandler
        :param fname: the file to store the help in, uses stdout if not provided
        :type fname: str
        """

        help = self._do_generate(handler)
        if fname is None:
            print(help)
        else:
            with open(fname, "w") as hf:
                hf.write(help)


def class_hierarchy_help(super_class: Any, generator: AbstractHelpGenerator, output_dir: str, module_regexp: str = None) -> Tuple[List[str], List[str]]:
    """
    Generates help files for all the classes of the specified class hierarchy
    and places them in the output directory.

    :param super_class: the super class of the hierarchy to generate the help files for
    :type super_class: type
    :param generator: the help generator to use
    :type generator: AbstractHelpGenerator
    :param output_dir: the output directory to place the files in
    :type output_dir: str
    :param module_regexp: regular expression to limit the modules to search in
    :type module_regexp: str
    :return: the tuple of list of classes and corresponding list of generated files, relative to the output directory (contains None if failed to generate a file)
    :rtype: tuple
    """
    classes = []
    file_names = []
    _classes = find_classes(super_class, use_cache=False, module_regexp=module_regexp)
    for cls in _classes:
        file_name = get_class_name(cls) + generator.file_extension()
        out_file = output_dir + "/" + file_name
        try:
            # skip abstract classes (just a naming convention)
            if cls.__name__.startswith("Abstract"):
                continue
            generator.generate(cls(), fname=out_file)
            classes.append(cls)
            file_names.append(file_name)
        except Exception:
            pass
    return classes, file_names
