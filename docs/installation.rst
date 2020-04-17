############
Installation
############

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

To install dob locally or to ensure it's up to date, simply run:

.. code-block:: sh

   $ pip3 install -U dob

Or run that command as superuser to install system-wide.

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
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.8 dob
    (dob) $ make develop

After creating the virtual environment,
run |workon|_ to start developing from a fresh terminal:

.. code-block:: sh

    $ workon dob
    (dob) $ dob --version
    ...

