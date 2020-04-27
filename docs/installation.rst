############
Installation
############

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

.. |py-downloads| replace:: Python downloads
.. _py-downloads: https://www.python.org/downloads/

``dob`` requires ``Python``, which is usually included by default in most
Linux distributions and macOS.

- If not, visit |py-downloads|_ and find the version suitable for your OS.

- See below for `installing on Windows`__.

Make sure you install Python 3, and not Python 2.

__ `Windows Install`_

User Install
============

To install ``dob`` locally or to ensure that it's up to date, simply run:

.. code-block:: sh

   $ pip3 install -U dob

- Note that on modern systems, where Python 2 is *not* installed or
  is not the default, a simple ``pip install dob`` should also work.

  - But using ``pip3`` ensures that this command works on all distros.

- You could also omit the ``-U`` upgrade flag, but dob is (currently,
  in 2020) under steady development, so you might want to periodically
  run the installer again to update to the latest release.

Update ``PATH``
---------------

- Hint: You might need to update ``PATH``, or to figure out where ``pip``
  installs ``dob`` to run it.

  E.g., on Linux, ``pip`` installs to ``~/.local/bin``, so you could
  either update ``PATH``::

    $ export PATH=$PATH:$HOME/.local/bin

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

Developer Install
-----------------

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

Windows Install
===============

.. |py-win-downloads| replace:: Python Releases for Windows
.. _py-win-downloads: https://www.python.org/downloads/windows/

You'll need to install Python before you can install ``dob`` on Windows.

Visit |py-win-downloads|_ and download a Python 3 installer.

- It's probably easiest to download the
  *Windows x86-64 executable installer*,
  or to just have your web browser run it.

- The *Windows x86-64 web-based installer* also
  works, but the executable installer is not a
  large download, and it seems to run faster.

- Note that the Python *2* installer will not work. Get Python *3*.

Run the Python 3 installer, and follow these instructions:

- At the bottom of the first wizard, make sure to select the PATH option:

  ☑ *"Add Python 3.8 to PATH"*

- Click *"Install Now"* (and wait a moment...)

- On the last wizard screen, make sure to click the disable option:

  Click *"Disable path length limit"*

- If you forget either of these steps, you can Uninstall Python,
  and then re-install it.

After installing Python, you'll install and run ``dob``
from Windows Powershell (or the old CMD prompt).

There are many ways to run Powershell, including:

- Click the Start Menu, type "powershell", and click
  "Windows Powershell" in the list.

- You can also press ``Windows-R`` to bring up the Run dialog,
  and then type "powershell" and press Enter. But note that
  running Powershell this way uses a larger font size than
  running the one in the Start Menu (at least in the author's
  experience).

You can now install and run dob from within Powershell, as
documented above. E.g.,

.. code-block:: sh

   $ pip3 install -U dob
   $ dob --version

- Note that Python also installs a few of its own items:

  | *Start Menu > Python 3.8 > IDLE (Python 3.8 64-bit)*
  | *Start Menu > Python 3.8 > Python 3.8 (64-bit)*

  but these bring up the
  `Python Interpreter <https://docs.python.org/3/tutorial/interpreter.html>`__.
  You don't want these.

- If you need more help on Windows, look at
  "`Installing Python 3 and PIP on Windows
  <https://www.scrapehero.com/how-to-install-python3-in-windows-10/>`__",
  or search the web.

