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


.. _structure:

Structure
=========

A ``serfnode`` powered container inherits from the ``serfnode`` image
and adds extra handlers and actors.
