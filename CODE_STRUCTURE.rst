Codebase Structure
==================

Here is a break down of all relevant files.

.. code:: bash

   ├── .coveragerc
   ├── .gitignore
   ├── .release
   ├── .travis.yml
   ├── LICENSE
   ├── MANIFEST.in
   ├── Makefile
   ├── README.rst
   ├── development.txt
   ├── docs
   │   ├── Makefile
   │   └── source
   │       ├── api.rst
   │       ├── conf.py
   │       ├── index.rst
   │       └── tutorial.rst
   ├── requirements.txt
   ├── setup.cfg
   ├── setup.py
   ├── tests
   │   ├── __init__.py
   │   ├── functional
   │   │   └── __init__.py
   │   └── unit
   │       └── __init__.py
   └── mercator
       ├── __init__.py
       └── version.py


setup.py
--------

Contains the python package metadata, making it installable as a
package and ready to be published in pypi.

For more information check the `setuptools documentation
<https://setuptools.readthedocs.io/en/latest/setuptools.html>`_.

setup.cfg
---------

`Configures nose <https://nose.readthedocs.io/en/latest/api/commands.html>`_ as a test runner, setting up code coverage check and report and other niceties.


requirements.txt
----------------

Declares the runtime dependencies of the python package ``mercator``

development.txt
---------------

Declares the local development dependencies for the project.


Makefile
--------

The `make <https://www.gnu.org/software/make>`_ tool is usually
available for MacOSX and most linux distributions by default making it
a decent candidate to automate the development workflow and make us
more productive in maintaining a robust codebase.

Below is a break down of each available target.

.. _make default:
``make`` or ``make default``
----------------------------

Alias for the targets :ref:`make dependencies`, :ref:`make tests` and :ref:`make docs`

.. _make dependencies:
``make dependencies``
---------------------

#. updates pip to the latest version
#. installs the contents of development.txt

.. _make develop:
``make develop``
----------------

Builds your python package and makes is available in the `PYTHONPATH
<https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`_.
Under the hood it runs ``python setup.py develop`` which is similar to
running ``pip install mercator`` except that
you can modify your code locally and the changes will be available
immediately.

.. _make tests:
``make tests``
--------------

Alias for the targets :ref:`make unit` and :ref:`make functional`

.. _make unit:
``make unit``
-------------

Runs `nose <https://nose.readthedocs.io/en/latest/>`_ against all test code under ``tests/unit``

.. _make functional:
``make functional``
-------------------

Like :ref:`make unit` but runs tests against ``tests/functional``

.. _make docs:
``make docs``
-------------

Builds the documentation as HTML.

To browse locally open the file ``docs/build/html/index.html``

.. _make release:
``make release``
----------------

#. Makes a new release of your package by running the :ref:`release script <release script>`
#. Runs :ref:`make pypi`

.. _make pypi:
``make pypi``
-------------

#. Builds a tarball with the new version
#. Publishes your package to pypi using `twine <https://pypi.org/project/twine/>`_

.. _make clean:
``make clean``
--------------

#. Removes all pre-compiled python files (``*.pyc``)
#. Removes build html documentation, any release tarballs and `egg-info <https://setuptools.readthedocs.io/en/latest/formats.html>`_


Dot-files in the project root
-----------------------------

.coveragerc
~~~~~~~~~~~

Tells the coverage module to report the line numbers `missing test coverage <https://coverage.readthedocs.io/en/coverage-4.5.1/config.html#report>`_.

.. code:: ini

   [report]
   show_missing = True


.gitignore
~~~~~~~~~~

Configures the files that `should not be kept under version control <https://git-scm.com/docs/gitignore>`_.

.. _release script:
.release
~~~~~~~~

A shell-script used by the Makefile target ``make release``, it will parse your library version from ``mercator/version.py``.
The script will interactively ask what should be the next version number, then will update it on the following files:

.. code:: bash

   ├── README.rst
   ├── docs
   │   └── source
   │       └── conf.py
   ├── setup.py
   └── mercator
       ├── __init__.py
       └── version.py


**IMPORTANT:** for this to work make sure to keep the version number compliant with `semantic versioning <https://semver.org/>`_: ``number.number.number``

.travis.yml
~~~~~~~~~~~

Configures `Travis CI <https://travis-ci.org>`_ to run the tests.

For more information check the Travis documentation on how to `build python projects <https://docs.travis-ci.com/user/languages/python/>`_ and configure a test matrix to `test your project against multiple python versions <https://docs.travis-ci.com/user/customizing-the-build#Explicitly-Including-Jobs>`_.
Bonus: setup `continuous delivery to pypi <https://docs.travis-ci.com/user/deployment/pypi/>`_
