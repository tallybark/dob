############
Installation
############

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

.. NOTE:: Please be aware that |dob|_ is currently *alpha* software.

          The application works well, but it has a few minor issues
          that must be fixed before it can be truly released. And it
          wouldn't hurt to write a few more tests and expand coverage.

          In lieu of committing to a date that this software will be
          out of alpha, let's just say, it'll happen this year, 2019!

To install system-wide, run as superuser

.. code-block:: sh

   $ pip3 install dob

To install user-local, simply run:

.. code-block:: sh

    $ pip3 install -U dob

To install within a |virtualenv|_, try:

.. code-block:: sh

    $ mkvirtualenv dob
    $ pip3 install dob

To develop on the project, link to the source files instead:

.. code-block:: sh

    $ deactivate
    $ rmvirtualenv dob
    $ git clone git@github.com:hotoffthehamster/dob.git
    $ cd dob
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.6 dob
    $ make develop

To start developing from a fresh terminal, run |workon|_:

.. code-block:: sh

    $ workon dob

