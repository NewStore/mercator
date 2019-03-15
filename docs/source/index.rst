.. Mercator - Data Mapper for Protobuf documentation master file, created with
   cookiecutter gh:gabrielfalcao/cookiecutter-from-editor-to-pypi

Mercator
========

Python DSL to leverage translation of dictionaries and SQLAlchemy into
Protobuf objects.

**Primarily created with the intention of migrating python services to support gRPC.**


Data Mapper for Protobuf
------------------------

This library is primarily intended to aid the migration of
python-based microservices to gRPC by leveraging a DSL that resembles
ORM and ActiveRecord patterns.

It supports mapping key/values from dictionaries to Protobuf 3 as well
as SQLAlchemy ORM models intro Protobuf 3.


Installing
~~~~~~~~~~

.. code:: bash

   pip install mercator


.. toctree::
   :maxdepth: 3
   :caption: Table of Contents:

   proto-mapping
   sqlalchemy-orm-support
   api
