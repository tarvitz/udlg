UDLG 
====

* UDLG is dialogs file format using in `Underrail <http://store.steampowered.com/app/250520/>`_ game.

.. contents:: :local:
    :depth: 2

File format specs
-----------------
Originally udlg uses Microsoft Binary Format Data Structure
you can know everything you need with
`specification documentation <https://msdn.microsoft.com/en-us/library/cc236844.aspx>`_

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

.. code-block:: bash
   user@localhost$ virtualenv --no-site-packages venv3 --python=python3.4
   user@localhost$ source venv3/bin/activate
   user@localhost$ pip install -r requirements/test.txt

Dependencies
~~~~~~~~~~~~
* python 3.4
* (explore.py uses python3.5)

On windows you would need to have lxml package you can take
`it here <http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml>`_

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

Documentation
-------------

- `Binary Format Data Structure <https://msdn.microsoft.com/en-us/library/cc236844.aspx>`_
