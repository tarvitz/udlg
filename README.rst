UDLG 
====

* UDLG is dialogs file format using in `Underrail <http://store.steampowered.com/app/250520/>`_ game.

.. contents:: :local:
    :depth: 2

File format templates
---------------------
File format templates stored inside ``templates`` directory and provides much
help in investigation udlg file format process.
Use `010editor <http://www.sweetscape.com/010editor/>`_ to process udlg files
with given templates.


Roadmap
-------
- Extract and store translations into *.udlg files

Library
-------
UDLG file support will be implement as `Python <https://www.python.org/>`_
application and available across
`PyPI <https://pypi.python.org/pypi>`_ as soon as first roadmap would
be achieved.

document build requirements stored in py3.txt

.. code-block:: bash
   user@localhost$ virtualenv --no-site-packages venv3
   user@localhost$ source venv3/bin/activate
   user@localhost$ pip install -r requirements/py3.txt

Dependencies
~~~~~~~~~~~~
* python 3.4
* (explore.py uses python3.5)

Tests
-----
There some tests covers utils, helps to maintain python library clean and
consistence.

Using tox
~~~~~~~~~
Using `tox <http://tox.testrun.org/>`_ is recommended way to run tests.
Just run (you should install tox before run it):

.. code-block:: bash

  user@localhost udlg$ tox

Scripts
-------
There're small amount of scripts now:

- ``explore.py`` - finds all *.udlg inside ``remote/Data/Dialogs`` folder. Please
  modify script or just copy whole Dialogs content to given path.

Temporary
~~~~~~~~~
There're temporarty scripts what provides some aggregation data process. They
could help to access some data.

- ``scripts/header_inspect.py`` shows first block data as hashmap (json dict).
- ``scripts/udlg_watch.py`` see next block after already investigated and aggregate
  differences into output.json file.

Documentation
-------------
Not yet ;)
