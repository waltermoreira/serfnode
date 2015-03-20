==========
 Serfnode
==========

Add serf powers to your containers.


Quickstart
==========

(Description of a simple example coming soon.)


File System API
===============

Serfnode keeps the information of the cluster in every member. It uses
a defined set of files in JSON format, both in the parent and in the
children.  There are two types of JSON objects with the following
schema:

- *Container info*: full information about a container and its id in
  the cluster:

  .. code-block:: json

     {
       "id": "<node id>",
       "inspect": {<output of docker inspect>}
     }

- *Node info*: information about a Serfnode as a member of the
  cluster:

  .. code-block:: json

     {
       "id": "<node id>",
       "role": "<role of member>",
       "ports": {<dict of port mappings>},
       "serf_ip": "<ip of serf agent>",
       "serf_port": "<port of serf agent>",
       "service_ip": "<ip of service>",
       "service_port": "<port of service>",
       "timestamp": "<unix timestamp of last member update>"
     }


Parent files
------------

The parent container has access to these files:

- ``/me.json`` (type *Container info*): information about itself as a
  container.

- ``/children_by_name.json`` (type dict of *Container info*):
  information about the children as containers.  The keys are the
  container names of the children.

- ``/serfnodes_by_id.json`` (type dict of *Node info*): information
  about the cluster.  The keys are the node id of the members.

- ``/serfnodes_by_role.json`` (type dict of list of *Node info*):
  information about the cluster classified by roles.  The keys are
  role names.  The values are lists of nodes having a given role.


Children files
--------------

Each child has access to these files:

- ``/me.json`` (type *Container info*): information about itself as a
  container.

- ``/serfnode/parent.json`` (type *Container info*): information about
  its parent as a container.

- ``/serfnode/serfnodes_by_{id,role}.json``: same as the files in the
  parent.


Event server
------------

Each child contains a file with name ``/serfnode/parent``.  The child
can write to this file for sending events to the cluster.  The file is
a named FIFO pipe, with the other end connected to the parent
container.  The parent reads from the pipe and uses the ``serf`` agent
to raise the event in the cluster.

The format for the message is a JSON object with the form:

.. code-block:: json

   ["<event_name>", {<payload>}]

The *payload* is an arbitrary JSON object that gets passed as argument
to the handler with name ``event_name`` in every member.


/etc/hosts
----------

Serfnode updates the ``/etc/hosts`` file of the parent and the
children to contain lines with the form::

    <role> <service ip>

When there are more than one member with the same role, Serfnode picks
the oldest one.


Building from source
====================

To build from source, clone this repository and build with Docker:

.. code-block:: bash

   $ git clone https://github.com/waltermoreira/serfnode.git
   $ cd serfnode/serfnode
   $ docker build -t adama/serfnode .
