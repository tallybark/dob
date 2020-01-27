############
Installation
############

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

To install system-wide, run as superuser:

.. code-block:: sh

   $ pip3 install dob

To install user-local, simply run:

.. code-block:: sh

    $ pip3 install -U dob

To install within a |virtualenv|_, try:

.. code-block:: sh

    $ mkvirtualenv dob
    (dob) $ pip3 install dob

To develop on the project, link to the source files instead:

.. code-block:: sh

    (dob) $ deactivate
    $ rmvirtualenv dob
    $ git clone git@github.com:hotoffthehamster/dob.git
    $ cd dob
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.6 dob
    (dob) $ make develop

After creating the virtual environment,
to start developing from a fresh terminal, run |workon|_:

.. code-block:: sh

    $ workon dob
    (dob) $ ...

