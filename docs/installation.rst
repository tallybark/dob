############
Installation
############

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

To install system-wide, run as superuser::

    $ pip3 install dob

To install user-local, simply run::

    $ pip3 install -U dob

To install within a |virtualenv|_, try::

    $ mkvirtualenv dob
    $ pip3 install dob

To develop on the project, link to the source files instead::

    $ deactivate
    $ rmvirtualenv dob
    $ git clone git@github.com:hotoffthehamster/dob.git
    $ cd dob
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.6 dob
    $ make develop

To start developing from a fresh terminal, run |workon|_::

    $ workon dob

