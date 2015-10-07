.. EMG-Visualization-Project documentation. Describes implementation of
   different modules, design descions. In summary the whole Software-Engineering
   stuff.

**************
Implementation
**************
This chapter explains the design of the solution, how different components
interact and what functionality is realized with them.

The solution comprises three major parts, going to be illustrated in detail
in following sections.

The first part is about representing an Experiment according to the
:ref:`chap-taxonomy`, the second part is about performing online learning
over the network using distributed data-sources and the third part deals
with streamlining operations on data.

=========================
Experiment Representation
=========================
Python is a powerful programming language providing a wide range of
libraries for data analysis and visualization. In particular the
`Pandas <http://pandas.pydata.org/>`_ library provides functionality for
analyzing time series data.

However, organizing all necessary information such as class labels, different
modalities, sessions, recordings and trials is not that convenient with pandas,
scipy and numpy alone.

The classes implemented in package ``model.model`` wrap functionality around
pandas and numpy to alleviate working with that specific data.

------------------------------------------
Defining an Experiment
------------------------------------------
The idea is to model an experiment similar to a knowledge base in prolog.
This knowledge base contains all information about trials in different
recordings or specific events within the trials and can be quried for those.

Things that are contained in the knowledge base are for example:

* The recording
* Start and duration of trials
* Start and duration of specific events
* Labels for trials
* Modalities and channels used
* Participating subjects

--------------------------------------
Managing Trials, Recordings and Events
--------------------------------------
Recordings are the only entities that hold a larger amount of data. During
definition, a recording object may be passed a DataFrame, Array or path to
a file containing the recording's data.

Trials are chunks of the recording. Each trial object holds a reference to
the recording it belongs to. When samples of a trial are requested, the
recording is sliced according to the start point and duration of the trial.

Similar, Events are defined for trials and specify a start point relative to
the start of the trial and optionally a duration.

The chunk of the recording is returned as an instance of class
``DataContainer``. This object then contains all necessary information such as
the events defined for the trial, sampling rate, names of channels and so on.

---------
Summary
---------
Representation of an experiment is a sort of knowledge base holding all
relevant information. It acts as a wrapper around pandas and numpy to allow
better handling of data in this setting.

===============================
Streamlining Data Preparation
===============================
The primary goal of this part is chaining of operations used for
data preparation.

The functionality is implemented using the :ref:`subsec-decorator-pattern`.
This design choice is motivated by allowing better implementation of more
complex functionality, a strong guideline how to implement new functions and
an elegant way of chaining different functions.

.. _subsec-decorator-pattern:
-----------------
Decorator Pattern
-----------------
This design pattern wraps an object and augments it with additional functionality
independently from other instances of the same class.

It allows division of functionality between classes, where each class has
a certain focus. Thus it is well suited in this case. In this context, each
class implements a certain data preparation functionality.

-------------------
Generator and Lists
-------------------
Each decorator class can act as a generator or simply returning a list of
``DataContainer``.

A generator in python is function that acts like an interator. This means,
the function returns elements lazily, that is on demand.

The ``WindowDecorator`` is a perfect example of this. When creating windows
from a sequence, new arrays are created. If windows are generated from multiple
sequences at once, a lot of memory might be used.

When using a generator, a new windows is created when explicitly asked for
leading to reduced memory usage.

--------
Summary
--------
By using the decorator pattern one class implements a specific function
related to data preparation. Different decorators can be stacked to chain
functions.

Decorators can act as generators, thus lowering the resource consumption.

===============
Online Learning
===============
This part explains functionality of working with distributed datasources and
sending it over the network.

------------------
Nanomsg and ZeroMQ
------------------
Nanomsg and ZeroMQ are both high performance, asynchroneous messaging libraries.
In fact, Nanomsg is the successor of ZeroMQ and developed by the same people.

Nanomsg and ZeroMQ abstract networking and allow easy implementation of (large)
distributed systems.

Both libraries implement a range of message patterns, such as the publisher-
subscriber pattern, being used in this implementation.

Nanomsg is newer and fixes some of the shortcomings of ZeroMQ. The support and
documentation of Nanomsg is not yet as good as the one for ZeroMQ, though.
Especially when it comes to working on windows, ZeroMQ is very convenient.

Both libraries are supported.

----------------------------------
From Datasource to Learning Scheme
----------------------------------
To work with distributed data the publisher-subscriber pattern is used. In this
pattern there is one information broker. This broker broadcasts messages to a
specific topic. After subscribing to a topic, the subscriber receives messages
from the respective publisher.

In this solution, the messages of the publisher are a specific modality. To
collect the data, ``DataSource`` objects are used. They retrieve data from
a real-time system and put them into a queue. The publisher grabs these
messages and publishs them into the network.

Somewehere else a subscriber listens for messages for his modality. If the
subscriber gets a message, the message is deserialized and put into a queue.

From there it can be fed into an online learning scheme.

