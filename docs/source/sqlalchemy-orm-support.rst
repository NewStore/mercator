.. _SQLAlchemy ORM Support:

.. _SQLAlchemy Support:

SQLAlchemy ORM Support
======================

Sometimes it can be useful to map SQLAlchemy ORM objects when
migrating other RPC implementations to gRPC.


On Power and Responsability
---------------------------

It is important to note that this practice can have pernicious effects
on the separation of responsability of your codebase.

ProtoMappings provide a powerful way to make this transition easier,
so use it wisely.


A simple recipe
---------------

This example was partially extracted from the functional tests and simplified for didactic purposes. There is `a more complete example on github. <https://github.com/NewStore/mercator/blob/master/tests/functional/test_sqlalchemy_orm_to_proto.py>`_

Here we simplified our recipe to a service to *"return user data from a SQL database"*

**Ingredients**
~~~~~~~~~~~~~~~

1. A SQLAlchemy model: ``User``
2. A Protobuf definition of a ``User`` message and a ``UserService``
3. The implementation of the python service that uses a
   ``UserMapping`` to map model fields into protobuf message fields.


A SQLAlchemy Model
~~~~~~~~~~~~~~~~~~


.. code-block:: python

   from sqlalchemy.ext.declarative import declarative_base


   MySimpleBaseModel = declarative_base()

   class User(MySimpleBaseModel):
       __tablename__ = 'user'
       __table_args__ = {'useexisting': True}

       id = sa.Column(
           postgresql.UUID(as_uuid=True),
           primary_key=True,
           default=uuid4
       )
       login = sa.Column(sa.String(256))
       email = sa.Column(sa.String(256))
       password = sa.Column(sa.String(256))


A protobuf declaration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: proto

   syntax = "proto3";
   package services.simple_example.sqlalchemy;

   message User {
     string uuid = 1;
     string username = 2;
     string email = 3;
   }

   message UserDataRequest {
       string user_uuid = 1;
   }

   service UserService {
       rpc GetUser (UserDataRequest) returns (User){};
   }


The service implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from . import user_pb2_grpc
   from . import sql

   class UserMapping(ProtoMapping):
       # the destination type, must come from a *_pb2.py file compiled from your *.proto file

       __proto__ = domain_pb2.User

       # the base type of your sqlalchemy types
       __source_input_type__ = sql.MySimpleBaseModel

       uuid = ProtoKey('id', str)    # translate "id" into "uuid"
       email = ProtoKey('email', str)
       username = ProtoKey('login', str) # translate "login" into "username"


   class business_logic:
       """isolates SQL queries returning objects
       ready for the protobuf serialization layer"""

       @staticmethod
       def get_user_by_uuid(uuid):
           result = sql.session.query(sql.User).where(sql.User.uuid==uuid)
           return result.one()


   class UserService(user_pb2_grpc.UserService):
       def GetUser(self, request, context):
           # retrieve sqlalchemy instance of user by uuid
           user = business_logic.get_user_by_id(request.user_uuid)

           return UserMapping(user).to_protobuf()
