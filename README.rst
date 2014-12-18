==========
 Serfnode
==========

Add serf powers to your containers.


Quickstart
==========

*Dependencies*: ``docker`` and ``fig``.

- Clone this repo and build the base image for the serfnodes:

  .. code-block:: bash

     $ git clone https://github.com/waltermoreira/serfnode.git
     $ cd serfnode/serfnode
     $ make

  This will generate an image with name ``serfnode``.

- Go to the ``example`` directory to see an example of use.  See
  `Structure`_ to read about its components.

  Build it and test it with:

  .. code-block:: bash

     $ cd ../example
     $ make
     $ fig up


Structure
=========

A ``serfnode`` powered container inherits from the ``serfnode`` image
and adds extra handlers and actors.

To write your own handlers, create the file ``handler/my_handler.py``
with a class inheriting from ``BaseHandler`` (see the example in the
``example/handler`` directory).

There are three kind of events:

- *supervisor events*: any change of state of processes in supervisor
  get broadcasted to the cluster via the ``supervisor`` event.  The
  payload includes information on the process, node, and change of
  state.

- *custom events*: arbitrary events defined by the user with arbitrary
  payload.  They are triggered by ``serf event`` or ``serf query``.

- *members joining/leaving/failing*: see ``serf`` for documentation.

Any serfnode also respond to two events: ``where`` and
``where_actors``, with information about the node ip and the actors
currently running in that node.


Actors
======

Actors can be defined in the file ``handler/actors.py`` (see example
in the ``example/handler`` directory), inheriting from
``ProcessActor`` or ``ThreadedActor``.
