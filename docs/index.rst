bottle-gui documentation
========================

Welcome in the bottle-gui documentation. This package is used to visualize
services used in bottle web framework.


User documentation
------------------

From the user's point of view, only thing you need to do is install the package
and import one function::

    pip install bottle-gui

And the code::

    from bottle_gui import bottle_gui

    gui = bottle_gui()

And thats it!

The :func:`bottle_gui` takes one optional parameter, which specifies where the
GUI service should run. By default, it will run at ``/``.


API documentation
-----------------

.. toctree::
    :maxdepth: 2

    api/modules


Testing
-------
This project uses `pytest <http://pytest.org>`_ for testing. You can run
the tests from the root of the package using following command::

    $ py.test

Which will output something like::

    $ py.test --pdb
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.6 -- py-1.4.23 -- pytest-2.6.0
    collected 2 items 

    tests/test_gui.py ..

    =========================== 2 passed in 1.31 seconds ==========================


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`