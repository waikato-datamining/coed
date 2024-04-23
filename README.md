# shallowflow-api
The API for shallowflow.

## Installation

Install via pip:

```bash
pip install "git+https://github.com/waikato-datamining/shallowflow-api.git"
```

## Classes

* Base classes

  * `shallowflow.api.actor.Actor`
  * `shallowflow.api.actor.InputConsumer`
  * `shallowflow.api.actor.OutputProducer`

* Boolean conditions

  * `shallowflow.api.condition.AbstractBooleanCondition`

* Configuration

  * `shallowflow.api.config.Option` - defines a single parameter
  * `shallowflow.api.config.OptionManager` - manages all parameters and conversion to/from dictionaries used in serialization
  * `shallowflow.api.config.AbstractOptionHandler` - ancestor for all classes that handler options

* Logging

  * `shallowflow.api.logging.LoggableObject`

* Help

  * `shallowflow.api.help.AbstractHelpGenerator` - ancestor

* Control actors

  * `shallowflow.api.control.ActorHandler` - manages multiple actors
  * `shallowflow.api.control.MutableActorHandler` - manages multiple actors, can be appended/removed
    
* Directors

  * `shallowflow.api.director.AbstractDirector` - used by `ActorHandler`

* Sources

  * `shallowflow.api.source.AbstractSimpleSource`
  * `shallowflow.api.source.AbstractListOutputSource` - can output items as list and one-by-one

* Transformers

  * `shallowflow.api.transformer.AbstractSimpleTransformer`
  * `shallowflow.api.transformer.AbstractListOutputTransformer` - can output items as list and one-by-one
    
* Sinks

  * `shallowflow.api.sink.AbstractSimpleSink`
  * `shallowflow.api.sink.AbstractFileWriter`


## Methods

* Serialization

  * `shallowflow.api.serialization.add_dict_reader` - add a handler for class to interpret a dictionary
  * `shallowflow.api.serialization.add_dict_writer` - add a handler for class to generate a dictionary
  * `shallowflow.api.serialization.get_dict_reader` - returns the handler for a class to interpret a dictionary
  * `shallowflow.api.serialization.get_dict_writer` - returns the handler for a class to generate a dictionary

* I/O

  * `shallowflow.api.io.add_flow_reader` - registers a handler for reading a new flow file format via the extension
  * `shallowflow.api.io.add_flow_writer` - registers a handler for writing a new flow file format via the extension
  * `shallowflow.api.io.load_actor` - loads an actor from a file, determines the reader based on the file extension
  * `shallowflow.api.io.save_actor` - saves an actor to a file, determines the writer based on the file extension

  Currently supported formats:
 
  * `.yaml`
  * `.json`
  * `.pkl` - object serialization via pickle
  