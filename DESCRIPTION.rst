The *Configurable Object Entry-point Discovery* Python3 library builds a registry
from objects that share a common superclass and which packages are defined in
the entry-points section of the `setup.py` file. This registry can then be
queried via the superclass and return all the located classes derived from it,
making it easy to manage a class hierarchy for plugins.

