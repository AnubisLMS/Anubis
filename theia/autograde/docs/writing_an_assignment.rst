=====================
Writing an Assignment
=====================

.. WARNING::
   These documentation along with the Anubis Shell Autograde library are a work in progress.
   Consider this a live document.

Declarative Configuration
=========================

Configuration is done in a mostly declarative way. This is done primarily for safety. By doing it this way,
we can significantly limit crashes that students see. The main idea is that something misconfigured can be deployed
without students seeing 500's or crash messages.

Declarative Components
======================

An assignment is made up of a list of exercises. These exercises are done in order by the student. In the configuration
file, this is represented by a python list of models as such:


.. code-block:: python
   :caption: Example minimal configuration

    import re
    from anubis_autograde.models import Exercise

    exercises: list[Exercise] = [
      Exercise(
          name='helloworld',
          command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"?'),
          output_regex=re.compile(r'[Hh]ello\s[Ww]orld!?'),
      ),
    ]

Exercise
--------

.. automodule:: anubis_autograde.models
   :members: Exercise

:py:class:`anubis_autograde.models.Exercise` is the main container class for assignments. Each
:py:class:`anubis_autograde.models.Exercise` object in the exercises
list will be another one in the sequence for students to complete.


.. code-block:: python
   :caption: Example minimal configuration

    Exercise(
       name='helloworld',
       command_regex=re.compile(r'echo \'?"?[Hh]ello\s[Ww]orld!?\'?"?'),
       output_regex=re.compile(r'[Hh]ello\s[Ww]orld!?'),
    )


ExistState
----------

Abstract condition declaratives will have a state attribute to denote if the underlying object the condition is
referencing should exist or not.

The simplest example of this is to set the state of a :py:class:`anubis_autograde.models.FileSystemCondition`
to be ``ExistState.ABSENT``. This means that when the condition is checked, the file should not exist. If it does,
then the exercise will not pass.

.. automodule:: anubis_autograde.models
   :members: ExistState


FileSystemCondition
-------------------

.. automodule:: anubis_autograde.models
   :members: FileSystemCondition


EnvVarCondition
---------------
.. automodule:: anubis_autograde.models
   :members: ExistState


Ejecting to python
==================

.. WARNING::
    While we recommend using the declarative approach for as many exercise types as possible, we recognise there are some
    places where ejecting to python may be necessary. We call this ejecting because that is exactly what it is. The code
    that you write here can easily break things. Guard rails and built in protections that you get from the declarative
    approach can basically be thrown out the window.


Creating an exercise that ejects to python is sometimes necessary. For this, you will need to write a function to eject
to. This function will take the :py:class:`anubis_autograde.models.Exercise` and
:py:class:`anubis_autograde.models.UserState` as parameters, and return a ``bool``. This ``bool`` should indicate
whether or not the exercise should be marked as completed.

.. code-block:: python
   :caption: Example ejection


    def eject_function(exercise: Exercise, user_state: UserState) -> bool:
       # do something we cannot do in the declarative approach
       # ...
       return True

    exercises: list[Exercise] = [
      Exercise(
          name='eject',
          eject_function=eject_function
      )
    ]

Debugging Exercises
===================

Workflow
--------

There are three things necessary to debug an assignment.

1. Generate an ``exercise.py`` file for your
   assignment. This will have all the code for the exercises you will be writing and debugging.
2. Leave an autograde server running in one terminal. Run this in the directory of your ``exercise.py``.
   The server is configured to restart when the ``exercise.py`` changes when run in debug mode.
3. Run the student shell in another terminal.

Generating exercise.py
----------------------

Make sure to be in the directory that you would like to drop your ``exercise.py`` file in. When you are there, run this
command to generate:

.. code-block:: sh
   :caption: Generate exercise.py

    anubis-autograde exercise-init

This step only needs to be performed once at the beginning of the assignment.


Debug Server
------------

Running the debug server:

.. code-block:: sh
   :caption: Run debug autograde server

    anubis-autograde --debug server exercise


Running the server with ``--debug`` ensures that any changes made to your ``exercise.py`` will be reloaded server
side (not in the shell). This will generate a ``.bashrc`` file in the current directory to be picked up when running
the debug shell.

Debug Shell
-----------

.. code-block:: sh
   :caption: Run debug shell

    anubis-autograde shell

