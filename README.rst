Mercator - Data Mapper for Protobuf
===================================

``version 0.1.11``

Python DSL to leverage translation of dictionaries and SQLAlchemy into Protobuf objects

.. image:: https://img.shields.io/pypi/pyversions/mercator.svg
   :target: https://pypi.python.org/pypi/mercator
   :alt: PyPi Project Page
.. image:: https://travis-ci.org/NewStore/mercator.svg?branch=master
   :target: https://travis-ci.org/NewStore/mercator
   :alt: Travis Build
.. image:: https://readthedocs.org/projects/mercator/badge/?version=latest
   :target: http://mercator.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://codecov.io/gh/NewStore/mercator/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/NewStore/mercator
   :alt: Test Coverage Reports


What is Mercator ?
------------------

Mercator is a Python library that simplifies the following of
serializing dictionary data into Protobuf binary data.

Mercator actually supports extracting data from:

- dictionaries
- SQLAlchemy model instances
- Any opaque python objects (e.g.: ``collections.namedtuple``)


When should I use Mercator ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- When migrating custom implementations of RPC to gGRPC.
- When migrating in-memory data to Protobuf.


When should I **not** use Mercator ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- When writing gRPC services from scratch.
- When writing anything that uses Protobuf gets called.


Install
-------

.. code:: bash

   pip install mercator


Documentation
-------------

`https://mercator.readthedocs.org <https://mercator.readthedocs.org>`_


Basic Usage
-----------


1. Given a protobuf declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: protobuf

   syntax = "proto3";
   package services.social_platform;

   import "google/protobuf/timestamp.proto";

   message User {
     message AuthToken {
       string value = 1;
       google.protobuf.Timestamp created_at = 2;
       google.protobuf.Timestamp expires_at = 3;
     }
   }


2. Declare Mappings
~~~~~~~~~~~~~~~~~~~

.. code:: python


   from mercator import (
       ProtoMapping,
       ProtoKey,
       ProtoList,
       SinglePropertyMapping,
   )
   from google.protobuf.timestamp_pb2 import Timestamp
   from google.protobuf.struct_pb2 import Struct
   from google.protobuf import struct_pb2


   ProtobufTimestamp = SinglePropertyMapping(int, Timestamp, 'seconds')

   class UserAuthTokenMapping(ProtoMapping):
       __proto__ = domain_pb2.User.AuthToken
       value = ProtoKey('data', str)
       created_at = ProtoKey('created_at', ProtobufTimestamp)
       expires_at = ProtoKey('expires_at', ProtobufTimestamp)


   class UserMapping(ProtoMapping):
       __proto__ = domain_pb2.User

       tokens = ProtoList('tokens', UserAuthTokenMapping)


3. Generate python files
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   python -m grpc_tools.protoc -I ./ --python_out=./ --grpc_python_out=./ ./*.proto


4. Process data!
~~~~~~~~~~~~~~~~

.. code:: python


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

   user = UserMapping(info).to_protobuf()

   assert isinstance(user, domain_pb2.User)


Contributing
------------

#. Check the `code structure documentation <https://github.com/NewStore/mercator/blob/master/CODE_STRUCTURE.rst>`_
#. Write tests
#. Write code
#. Send a pull-request
