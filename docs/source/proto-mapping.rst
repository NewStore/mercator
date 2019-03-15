.. _Proto Mapping:


Proto Mapping in Detail
=======================


A :py:class:`~mercator.ProtoMapping` provides syntax sugar to define
ways in which python dictionaries or objects can have its keys or
properties serialized into predefined ProtoBuf messages.


``__proto__``
-------------

Every :py:class:`~mercator.ProtoMapping` must declare a ``__proto__`` attribute that points to a valid :py:class:`~google.protobuf.message.Message` subclass.

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


.. warning:: Failing to declare a valid ``__proto__`` attribute will cause mercator to raise a :py:class:`SyntaxError`


``__source_input_type__``
-------------------------

**If declared,** this property will be considered as base-class of
 opaque objects that can have its properties mapped into protobuf.

 This feature was primarily designed to support `SQLAlchemy ORM <https://docs.sqlalchemy.org/en/latest/orm/>`_ models out of the box.


.. code:: python

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
             how to use the ``__source_input_type`` attribute.
