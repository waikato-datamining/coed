# coed
Configurable Object Entry-point Discovery.

## Installation

Install via pip:

```bash
pip install "git+https://github.com/waikato-datamining/coed.git"
```

## Usage

Approach:

1. define a class lister function
2. reference this function in `setup.py`
3. create a custom registry
4. query classes

For the examples below, we assume that the project is called `project42`.

### Class lister function

The class lister function simply returns a dictionary of super classes 
associated with lists of packages that classes derived from these super 
classes may occur in. 

For example, the following function is located in module `project42.class_lister`:

```python
from typing import List, Dict

def list_classes() -> Dict[str, List[str]]:
    return {
        "project42.superclass.One": [
            "project42.one",
            "project42.two",
        ],
        "project42.superclass.Two": [
            "project42.deep.deeper.deepest.another",
        ],
        "project42.superclass.Three": [
            "project42.one",
            "project42.three",
            "project42.deep.four",
            "project42.five",
        ],
    }
```

### Entry point in setup.py

The format for referencing the class lister function is as follows:

```
    ...
    entry_points={
        "class_lister": [
            "unique_name=module_name:function_name",
        ],
    },
    ...
```

The above example class lister function would be referenced like this:

```
    ...
    entry_points={
        "class_lister": [
            "project42=project42.class_lister:list_classes",
        ],
    },
    ...
```

### Custom registry

Create a custom registry (module `project42.registry`):

```python
from coed.registry import Registry as CRegistry

ENV_CLASSLISTERS = "PROJECT42_CLASSLISTERS"

class Registry(CRegistry):
    """
    Registry for managing plugins.
    """

    def __init__(self):
        super().__init__(env_class_listers=ENV_CLASSLISTERS)


REGISTRY = Registry()
```

**Notes** 
The environment variable is useful while developing, as the entrypoints
are only available when installing the library.

While developing in your IDE, you can set the `PROJECT42_CLASSLISTERS`
environment variable to list all your class lister functions (comma-separated list),
e.g.:

```
PROJECT42_CLASSLISTERS=project42.class_lister:list_classes
```

### Query classes

With the registry in place, you can now obtain all the classes that have been 
associated with a certain super class, e.g.:

```python
from project42.registry import REGISTRY

classes = REGISTRY.classes("project42.superclass.One")
for c in classes:
    print(c)
```
