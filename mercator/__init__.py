# -*- coding: utf-8 -*-
# <Mercator - Python DSL for Protobuf data mapping>
# Copyright (C) <2019>  NewStore Inc <engineering@newstore.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# from google.protobuf.message import Message
from .meta import MetaMapping
from .meta import FieldMapping
from .meta import MercatorDomainClass
# from .meta import BASE_MODEL_CLASS_REGISTRY
from .errors import TypeCastError
from .errors import ProtobufCastError


class SinglePropertyMapping(MercatorDomainClass):
    """creates a new instance of the given protobuf type populated with a
    single property preprocessing the input value with the given callable.

    Usage example:

    .. code:: python

       from mercator import (
           ProtoMapping,
           ProtoKey,
           SinglePropertyMapping,
       )
       from google.protobuf.timestamp_pb2 import Timestamp

       ProtobufTimestamp = SinglePropertyMapping(int, Timestamp, 'seconds')

       class UserAuthTokenMapping(ProtoMapping):
           __proto__ = domain_pb2.User.AuthToken
           value = ProtoKey('data', str)
           created_at = ProtoKey('created_at', ProtobufTimestamp)
           expires_at = ProtoKey('expires_at', ProtobufTimestamp)


        auth_token = UserAuthTokenMapping({'created_at': 12345}).to_protobuf()

        assert isinstance(auth_token.created_at, Timestamp)
        assert auth_token.created_at.seconds == 12345
    """
    def __init__(self, to_python, pb2_type, argname):
        self.to_python = to_python
        self.message_type = pb2_type
        self.argname = argname

    def __call__(self, value):
        params = {}
        input_value = self.to_python(value)
        params[self.argname] = input_value
        return self.message_type(**params)


class ProtoKey(FieldMapping):
    """Represents the intent to translate a object property or dictionary
    key into a protobuf message.

    Use this to map specific values into a protobuf object.

    Example:

    .. code:: python

       class UserMapping(ProtoMapping):
           __proto__ = domain_pb2.User

           username = ProtoKey('login', str)

    """
    def cast(self, value):
        if value is None:
            return

        result = super().cast(value)
        if not isinstance(result, ProtoMapping):
            return result

        return result.to_protobuf()


class ProtoList(FieldMapping):
    """Represents the intent to translate a several object properties or dictionary
    keys into a list in a protobuf message.


    Example:

    .. code:: python

       class UserMapping(ProtoMapping):
           __proto__ = domain_pb2.User

           tokens = ProtoList('tokens', UserAuthTokenMapping)
    """
    def cast(self, value):
        result = super().cast(value)

        if result is None:
            return

        if not isinstance(value, (list, tuple)):
            raise TypeCastError(f'ProtoList.cast() received a non-list value (type {type(value).__name__}): {value}')

        if issubclass(self.target_type, ProtoMapping):
            return [self.target_type(item).to_protobuf() for item in value]

        return result


def extract_fields_from_dict(data, names):
    return dict([(name, target.cast(data.get(target.name_at_source))) for name, target in names.items()])


def extract_fields_from_object(data, names):
    return dict([(name, target.cast(getattr(data, target.name_at_source, None))) for name, target in names.items()])


class ProtoMapping(object, metaclass=MetaMapping):
    """Base class to define attribute mapping from :py:class:`dict` or
    :py:class:`sqlalchemy.ext.declarative.api.Base` instances into
    pre-filled protobuf messages.

    Usage example:

    .. code:: python

       from mercator import (
           ProtoMapping,
           ProtoKey,
           ProtoList,
           SinglePropertyMapping,
       )
       from google.protobuf.timestamp_pb2 import Timestamp

       ProtobufTimestamp = SinglePropertyMapping(int, Timestamp, 'seconds')

       class AuthRequestMapping(ProtoMapping):
           __proto__ = domain_pb2.AuthRequest

           username = ProtoKey('username', str)
           password = ProtoKey('password', str)


       class UserAuthTokenMapping(ProtoMapping):
           __proto__ = domain_pb2.User.AuthToken
           value = ProtoKey('data', str)
           created_at = ProtoKey('created_at', ProtobufTimestamp)
           expires_at = ProtoKey('expires_at', ProtobufTimestamp)


       class UserMapping(ProtoMapping):
           __proto__ = domain_pb2.User

           uuid = ProtoKey('id', str)
           email = ProtoKey('email', str)
           username = ProtoKey('login', str)
           tokens = ProtoList('tokens', UserAuthTokenMapping)
           metadata = ProtoKey('extra_info', dict)


       class MediaMapping(ProtoMapping):
           __proto__ = domain_pb2.Media

           author = ProtoKey('author', UserMapping)
           download_url = ProtoKey('link', str)
           blob = ProtoKey('blob', bytes)
           content_type = ProtoKey('content_type', bytes)


       class AuthResponseMapping(ProtoMapping):
           __proto__ = domain_pb2.AuthResponse

           token = ProtoKey('token', UserAuthTokenMapping)
    """
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        if self.data is None:
            return {}

        fields = self.__fields__
        if isinstance(self.data, dict):
            return extract_fields_from_dict(self.data, fields)

        elif isinstance(self.data, self.BaseModelClass):
            return extract_fields_from_object(self.data, fields)

        else:
            raise TypeError(f'{self.data} must be a dict or {self.BaseModelClass} but is {type(self.data)} instead')

    def to_protobuf(self):
        data = self.to_dict()
        try:
            return self.__proto__(**data)
        except ValueError as e:
            message = str(e)
            raise ProtobufCastError(f'{message} when casting {self.__proto__} with data: {data}')
