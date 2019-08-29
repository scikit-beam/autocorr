============
Installation
============

Installation Using Pip
======================

This library has not yet been released on PyPI, so must be installed from
source.

.. code:: bash

   git clone https://github.com/scikit-beam/autocorr
   cd autocorr
   # First install pybind11, a build-time dependency.
   pip install pybind11
   # Install the package and all its run-time dependencies.
   pip install -e .

You may also wish to install matplotlib. It is not a required dependency, but
it is used in our examples for visualizing results.

.. code:: bash

   pip install matplotlib

Development
===========

For development, you will also want the dependencies for running the tests and
building the documentation:

.. code-block:: bash

    pip install -Ur requirements-dev.txt

To run the tests:

.. code-block:: bash

    pytest

You should see output ending in "<X> passed in <Y> seconds". For debugging,
these optional arguments to ``pytest`` are commonly useful:

* ``-v`` verbose
* ``-s`` Do not capture stdout/err per test.
* ``-k EXPRESSION`` Filter tests by pattern-matching test name.

To build this documentation on your local machine, run

.. code-block:: bash

    make -C docs html

which will create a subdirectory of HTML files at ``docs/build/html``. Open
``docs/build/html/index.html`` in your browser view the rendered documentation.
