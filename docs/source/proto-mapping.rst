.. _Proto Mapping:


Proto Mapping in Detail
=======================


A :py:class:`~mercator.ProtoMapping` provides syntax sugar to define
ways in which python dictionaries or objects can have its keys or
properties serialized into predefined ProtoBuf messages.


.. _proto:

``__proto__``
-------------

Every :py:class:`~mercator.ProtoMapping` must declare a :ref:`proto` attribute that points to a valid :py:class:`~google.protobuf.message.Message` subclass.

Example:
~~~~~~~~

.. code-block:: python
   :emphasize-lines: 8

   from google.protobuf.timestamp_pb2 import Timestamp

   from mercator import ProtoMapping
   from mercator import ProtoKey


   class TimestampMapping(ProtoMapping):
       __proto__ = Timestamp

    seconds = ProtoKey('seconds', int)


.. warning:: Failing to declare a valid :ref:`proto` attribute will cause mercator to raise a :py:class:`SyntaxError`

.. _source-input-type:

``__source_input_type__``
-------------------------


**If declared**, this property will be considered as base-class of opaque objects that can have its properties mapped into protobuf.

This feature was primarily designed to support `SQLAlchemy ORM models <https://docs.sqlalchemy.org/en/latest/orm/>`_ out of the box but supports any opaque python objects, as long as their base classes are defined by this attribute.

.. code-block:: python
   :emphasize-lines: 20

   from sqlalchemy.ext.declarative import declarative_base

   from mercator import ProtoMapping
   from mercator import ProtoKey


   MySimpleBaseModel = declarative_base()

   class User(MySimpleBaseModel):
       __tablename__ = 'user'
       __table_args__ = {'useexisting': True}

       login = sa.Column(sa.String(256))
       email = sa.Column(sa.String(256))
       password = sa.Column(sa.String(256))


   class UserMapping(ProtoMapping):
       __proto__ = domain_pb2.User
       __source_input_type__ = User


.. important:: This attribute is optional when declaring proto mappings, but if defined it must be a :py:class:`type`.


.. seealso:: The section :ref:`SQLAlchemy Support` for more information on
             how to use the ``__source_input_type__`` attribute.


.. _field mapping:

Field mappings
--------------

Field mappings are either :py:class:`~mercator.ProtoKey` or
:py:class:`~mercator.ProtoList` class-attributes defined in the body
of your :py:class:`~mercator.ProtoMapping` subclass.

This gives you the power to gather data from dictionaries with keys
that are different than in the protobuf model.


.. _target-type:

``target_type``
~~~~~~~~~~~~~~~

Field mappings are subclasses of :py:class:`mercator.meta.FieldMapping` and share its ``__init__`` signature:

.. code-block:: python

   FieldMapping(name_at_source: str, target_type: type)

   ProtoKey(name_at_source: str, target_type: type)

   ProtoList(name_at_source: str, target_type: type)

The ``target_type`` argument is optional, but when given, supports different types.

Let's dive into the possibilities.

.. _target-type-native:

Native python types
~~~~~~~~~~~~~~~~~~~

Ensures that the field value is cast into any python type, namely: :py:class:`str`, :py:class:`int`, :py:class:`float`, :py:class:`long`, :py:class:`dict`, :py:class:`list`


Mappings of Mappings
~~~~~~~~~~~~~~~~~~~~

Allows recursively translating data into protobuf messages whose
members contain sub-messages.


Example
.......

.. code-block:: python
   :emphasize-lines: 20

   from mercator import (
       ProtoMapping,
       ProtoKey,
   )
   from . import domain_pb2
   from . import sql


   class UserMapping(ProtoMapping):
       __proto__ = domain_pb2.User

       uuid = ProtoKey('id', str)
       email = ProtoKey('email', str)
       username = ProtoKey('login', str)


   class MediaMapping(ProtoMapping):
       __proto__ = domain_pb2.UserMedia

       author = ProtoKey('owner', UserMapping)
       download_url = ProtoKey('link', str)
