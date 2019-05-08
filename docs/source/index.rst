.. Mercator - Data Mapper for Protobuf documentation master file, created with
   cookiecutter gh:gabrielfalcao/cookiecutter-from-editor-to-pypi

Mercator
========

Python DSL to leverage translation of dictionaries and SQLAlchemy into
Protobuf objects.

**Primarily created with the intention of migrating python services to support gRPC.**


What is Mercator ?
------------------

Mercator is a Python library that simplifies the following of
serializing dictionary data into Protobuf binary data.

Mercator actually supports extracting data from:

- dictionaries
- SQLAlchemy model instances
- Any opaque python objects (e.g.: :py:func:`~collections.namedtuple`)


When should I use Mercator ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- When migrating custom implementations of RPC to gGRPC.
- When migrating in-memory data to Protobuf.


When should I **not** use Mercator ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- When writing gRPC services from scratch.
- When writing anything that uses Protobuf gets called.


A Data Mapper for Protobuf
--------------------------

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



Example Usage
-------------

.. code:: python

   from myproject.mappings import (
       UserMapping,
   )

   from . import avengers_pb2


   class AvengersService(avengers_pb2.HeroServicer):
       def GetHulk(self):
           info = {
               'login': 'Hulk',
               'email': 'bruce@avengers.world',
               'tokens': [
                   {
                       'data': 'this is the token',
                       'created_at': 1552240433,
                       'expires_at': 1552240733,
                   }
               ],
           }
           return UserMapping(info).to_protobuf()
