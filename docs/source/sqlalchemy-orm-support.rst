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


Full example: ORM Relationships
-------------------------------

.. warning:: while entirely supported, this feature can have
            pernicious impact in the coupling of SQL data model with
            gRPC protobuf data modeling. Use with caution.


The SQL Models
~~~~~~~~~~~~~~


.. code-block:: python
   :emphasize-lines: 44-49, 61-66

   from uuid import uuid4
   import sqlalchemy as sa
   from sqlalchemy import orm as sa_orm
   from sqlalchemy.dialects import postgresql
   from sqlalchemy.ext.declarative import declarative_base


   BaseModel = declarative_base()


   def PrimaryKeyUUID():
       return sa.Column(
           postgresql.UUID(as_uuid=True),
           primary_key=True,
           default=uuid4
       )


   class User(BaseModel):
       __tablename__ = 'user'
       __table_args__ = {'useexisting': True}

       uuid = PrimaryKeyUUID()
       login = sa.Column(sa.String(256))
       email = sa.Column(sa.String(256))
       password = sa.Column(sa.String(256))
       extra_info = sa.Column(
           postgresql.JSON,
           nullable=True,
       )


   class AuthToken(BaseModel):
       __tablename__ = 'auth_token'
       __table_args__ = {'useexisting': True}

       uuid = PrimaryKeyUUID()
       data = sa.Column(sa.String(256))
       created_at = sa.Column(sa.Integer)
       owner_id = sa.Column(
           postgresql.UUID(as_uuid=True),
           sa.ForeignKey('User.uuid')
       )
       owner = sa_orm.relationship(
           User,
           primaryjoin='and_(User.uuid == foreign(AuthToken.owner_id))',
           backref='tokens',
           uselist=False,
       )


   class Media(BaseModel):
       __tablename__ = 'media'
       __table_args__ = {'useexisting': True}

       uuid = PrimaryKeyUUID()
       author_id = sa.Column(
           postgresql.UUID(as_uuid=True),
           sa.ForeignKey('User.uuid')
       )
       author = sa_orm.relationship(
           User,
           primaryjoin='and_(Media.author_id == foreign(User.uuid))',
           backref='media',
           uselist=False,
       )
       url = sa.Column(sa.String(256))


Protobuf declaration
~~~~~~~~~~~~~~~~~~~~

For consistency with code examples let's consider this is saved with
``social_platform.proto`` and subsequently compiled to python with:

.. code-block:: bash

   python -m grpc_tools.protoc -I ./ \
       --python_out=./
       --grpc_python_out=./
       ./social_platform.proto

.. code-block:: proto
   :emphasize-lines: 31,38

   syntax = "proto3";
   package services.social_platform;

   import "google/protobuf/timestamp.proto";
   import "google/protobuf/struct.proto";

   service Auth {
     // returns an User.AuthToken
     rpc AuthenticateUser (AuthRequest) returns (AuthResponse){};
   }

   message AuthRequest {
     string username = 1;
     string password = 2;
   }
   message AuthResponse {
     User.AuthToken token = 1;
   }


   message User {
     message AuthToken {
       string value = 1;
       google.protobuf.Timestamp created_at = 2;
       google.protobuf.Timestamp expires_at = 3;
     }

     string uuid = 1;
     string username = 2;
     string email = 3;
     repeated AuthToken tokens = 4;
     google.protobuf.Struct metadata = 5;
   }

   message UserMedia {
     string uuid = 1;
     string name = 2;
     User author = 3; // the author of the media
     string download_url = 4; // the URL where the media can be downloaded
     bytes blob = 5; // the media itself, if available.

     enum ContentType {
       BLOG_POST = 0;
       IMAGE = 1;
       VIDEO = 2;
       QUOTE = 3;
       GIF = 4;
     }
     ContentType content_type = 4;
   }

   message MediaRequest {
      string media_uuid = 1;
      string media_name = 2;
   }

   service Media {
      rpc GetMedia (MediaRequest) returns (UserMedia){};
   }


Service Implementation with Mappings of Mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :emphasize-lines: 31-32, 42, 50, 59

   import grpc

   from mercator import (
       ProtoMapping,
       ProtoKey,
       ProtoList,
       SinglePropertyMapping,
   )
   from google.protobuf.timestamp_pb2 import Timestamp
   from concurrent.futures import ThreadPoolExecutor

   from . import social_platform_pb2
   from . import social_platform_pb2_grpc
   from . import sql


   ProtobufTimestamp = SinglePropertyMapping(int, Timestamp, 'seconds')

   class AuthRequestMapping(ProtoMapping):
       __proto__ = social_platform_pb2.AuthRequest

       username = ProtoKey('username', str)
       password = ProtoKey('password', str)


   class UserAuthTokenMapping(ProtoMapping):
       __proto__ = social_platform_pb2.User.AuthToken
       __source_input_type__ = sql.AuthToken

       value = ProtoKey('data', str)
       created_at = ProtoKey('created_at', ProtobufTimestamp)
       expires_at = ProtoKey('expires_at', ProtobufTimestamp)


   class UserMapping(ProtoMapping):
       __proto__ = social_platform_pb2.User
       __source_input_type__ = sql.User

       uuid = ProtoKey('id', str)
       email = ProtoKey('email', str)
       username = ProtoKey('login', str)
       tokens = ProtoList('tokens', UserAuthTokenMapping)
       metadata = ProtoKey('extra_info', dict)


   class MediaMapping(ProtoMapping):
       __proto__ = social_platform_pb2.UserMedia
       __source_input_type__ = sql.Media

       author = ProtoKey('author', UserMapping)
       download_url = ProtoKey('link', str)
       blob = ProtoKey('blob', bytes)
       content_type = ProtoKey('content_type', bytes)


   class AuthResponseMapping(ProtoMapping):
       __proto__ = social_platform_pb2.AuthResponse

       token = ProtoKey('token', UserAuthTokenMapping)


   class MediaRequestMapping(ProtoMapping):
       __proto__ = social_platform_pb2.MediaRequest


   class MediaServicer(social_platform_pb2_grpc.MediaServicer):
       def GetMedia(self, request, context):
           media = business_logic_module.retrieve_media_from_sqlalchemy(
               uuid=request.media_uuid,
               name=request.media_name,
           )

           return MediaMapping(media).to_protobuf()


   server = grpc.server(
       ThreadPoolExecutor(max_workers=10)
   )


   social_platform_pb2_grpc.add_MediaServicer_to_server(MediaServicer(), server)
