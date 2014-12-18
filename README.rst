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
     # Launch a node with role "exampleA"
     $ ROLE=exampleA fig -p exampleA up

  (the ``-p`` parameter is only to overwrite the default project name
  and to avoid collision when starting another node from the same
  directory.)

- We can test another nodes joining by starting the same container
  with a different role.

  First we get the contact information for the node we just started:

  .. code-block:: bash

     $ docker exec exampleA_example_1 cat /node_info
     {"node": "13024227bdce4a3682c482ab0cbfd89e", "bind_port": 7946,
     "advertise": "172.17.0.111", "rpc_port": 7373}

  We start a new node with:

  .. code-block:: bash

     $ ROLE=exampleB CONTACT=172.17.0.111:7946 fig -p exampleB up

  We now can check that the nodes are joined:

  .. code-block:: bash

     $ docker exec -it exampleA_example_1 bash
     root@b87605caaadd:/# serf members
     0b2c3818c9f94fb692a839c1b92de154  172.17.0.112:7946  alive  bind=7946,rpc=7373,role=exampleB,adv=172.17.0.112
     13024227bdce4a3682c482ab0cbfd89e  172.17.0.111:7946  alive  role=exampleA,adv=172.17.0.111,bind=7946,rpc=7373

  The ``supervisor`` events received by serf can be seen in
  ``/var/log/supervisor/serfnode-*``.

  The events can also be triggered with:

  .. code-block:: bash

     root@b87605caaadd:/# serf query where '{"role":"exampleB"}'
     Query 'where' dispatched
     Ack from '13024227bdce4a3682c482ab0cbfd89e'
     Ack from '0b2c3818c9f94fb692a839c1b92de154'
     Response from '0b2c3818c9f94fb692a839c1b92de154': {"ip": "172.17.0.112", "advertise": "172.17.0.112", "rpc": "7373", "bind": "7946"}

     SUCCESS
     Total Acks: 2
     Total Responses: 1
     root@b87605caaadd:/#

  The ``where`` event was answered only by the matching role node.  By
  default, all the nodes respond the events, for example:

  .. code-block:: bash

     root@b87605caaadd:/# serf query hello '{"who":"Walter"}'
     Query 'hello' dispatched
     Ack from '13024227bdce4a3682c482ab0cbfd89e'
     Ack from '0b2c3818c9f94fb692a839c1b92de154'
     Response from '0b2c3818c9f94fb692a839c1b92de154': Hello there, Walter!

     SUCCESS
     Response from '13024227bdce4a3682c482ab0cbfd89e': Hello there, Walter!

     SUCCESS
     Total Acks: 2
     Total Responses: 2
     root@b87605caaadd:/#



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
``where_actor``, with information about the node ip and the actors
currently running in that node.


Actors
======

Actors can be defined in the file ``handler/actors.py`` (see example
in the ``example/handler`` directory), inheriting from
``ProcessActor`` or ``ThreadedActor``.

Schedule actors to start at startup time by adding them to
supervisor.  The ``ExampleActor`` in ``example/handler/actors.py``
gets scheduled with the following file added to
``/etc/supervisor/conf.d/``:

.. code-block::

   # file: example.conf
   [program:example]
   command=/handler/start_actor.py ExampleActor
   autostart=true
   autorestart=true
