UDLG 
====

* UDLG is dialogs file format using in `Underrail <http://store.steampowered.com/app/250520/>`_ game.
You can use this tiny and small library to extract dialogs from *.udlg files and store your version into them.

Please see for scripts directory content for that purpose.
Apparently you'd be available to make simple translation for the game for any language that supports UTF-8.

.. contents:: :local:
    :depth: 2

.. note::

    This library isn't under maintenance. Though it could work with the latest version of udlg files and Underrail game itself.
    Please don't rely too much on current codebase ;)

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

Library
-------
Simple support for extracting dialogs data and the way to store it already implemented.
No further actions will needed after translation is done.

Here you can see translation topic. http://www.zoneofgames.ru/forum/index.php?showtopic=33279 (discussion goes in russian)

Installation
------------

.. code-block:: bash
   user@localhost$ virtualenv --no-site-packages venv3 --python=python3.4
   user@localhost$ source venv3/bin/activate
   user@localhost$ pip install -r requirements/test.txt

Dependencies
~~~~~~~~~~~~
`Python <https://www.python.org/downloads/>`_

Works on:

- python-3.4
- python-3.5

Windows, Linux, (probably Mac too)

**Would not work** on *python-2.7* and lower

Tests
-----
On windows you would need to have lxml package you can take
`it here <http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml>`_

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
