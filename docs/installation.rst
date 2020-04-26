############
Installation
############

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

User Install
============

To install ``dob`` locally or to ensure that it's up to date, simply run:

.. code-block:: sh

   $ pip3 install -U dob

- Note that on modern systems, where Python 2 is *not* installed or
  is not the default, a simple ``pip install dob`` should also work.

  - But using ``pip3`` ensures that the command works on all distros.

- You could also omit the ``-U`` upgrade flag, but dob is (currently,
  in 2020) under steady development, so you might want to periodically
  run the installer again to update to the latest release.

Update ``PATH``
---------------

- Hint: You might need to update ``PATH``, or to figure out where ``pip``
  installs ``dob`` to run it.

  E.g., on Linux, ``pip`` installs to ``~/.local/bin``, so you could
  either update ``PATH``::

    export PATH=$PATH:$HOME/.local/bin

  or you could just run ``~/.local/bin/dob`` directly.

  - When you install ``dob``, check the output for any "WARNING"
    messages that might tell you which directory to add to ``PATH``.

- For instance, on a fresh install of Linux, one might run the
  following commands to install ``dob``, update the user's ``PATH``,
  create a new config file and database, and run the interactive
  editor::

   $ pip3 install -U dob
   $ export PATH=$PATH:$HOME/.local/bin
   $ dob init
   $ dob edit

- Obviously, you'll want to add the ``export PATH`` command to
  your user's shell startup scripts so that you do not have to
  run this command every time you create a new shell session.

System Install
==============

Run ``pip`` as superuser to install system-wide. E.g.,:

.. code-block:: sh

   $ sudo pip3 install -U dob

(You should not need to update ``PATH`` after a system-wide install.)

Virtual Environment Install
===========================

To install within a |virtualenv|_, try:

.. code-block:: sh

    $ mkvirtualenv dob
    (dob) $ pip3 install dob

(The ``dob`` executable should be available immediately, regardless of ``PATH``.)

To develop on the project, link to the source files instead:

.. code-block:: sh

    (dob) $ deactivate
    $ rmvirtualenv dob
    $ git clone git@github.com:hotoffthehamster/dob.git
    $ cd dob
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.8 dob
    (dob) $ make develop

After creating the virtual environment,
run |workon|_ to start developing from a fresh terminal:

.. code-block:: sh

    $ workon dob
    (dob) $ dob --version
    ...

