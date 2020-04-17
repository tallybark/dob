###########
Basic Usage
###########

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

Start Fresh
-----------

Create the config and database:

.. code-block:: Bash

   $ dob init

Launch the interactive editor:

.. code-block:: Bash

   $ dob edit

.. _upgrade-legacy-database:

Upgrade Hamster
---------------

If you've been using Legacy Hamster, you can upgrade your
existing database, and then run the interactive editor:

.. code-block:: Bash

   $ legacy_db="~/.local/share/hamster-applet/hamster.db"
   $ dob store upgrade-legacy "$legacy_db"
   $ dob edit

More Help
---------

|dob|_ recognizes standard CLI flags, such as ``--help``:

.. code-block:: Bash

   $ dob -h
   Usage: dob [OPTIONS] COMMAND [ARGS]...

     dob is a time tracker for the command line.

     ...

Show Paths
----------

To see the path to the configuration file and data store,
use the ``details`` command:

.. code-block:: Bash

   $ dob details
   You are running dob version 3.0.0
   Configuration file at: /home/user/.config/dob/dob.conf
   Plugins directory at: /home/user/.config/dob/plugins
   Logfile stored at: /home/user/.cache/dob/log/dob.log
   Reports exported to: /home/user/.local/share/dob/export.{format}
   Using sqlite on database: /home/user/.local/share/dob/dob.sqlite

