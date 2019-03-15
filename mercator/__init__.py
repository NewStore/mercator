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

    Example:

    .. code-block:: python
       :emphasize-lines: 8, 13-14

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

    :param name_at_source: a string with the name of key or property to be extracted in an input object before casting into the target type.
    :param target_type: an optional :py:class:`~mercator.ProtoMapping` subclass or native python type. Check :ref:`target-type` for more details.
    """
    def cast(self, value):
        """
        :param value: a python object that is compatible with the given ``target_type``
        :returns: ``value`` coerced into the target type. Supports ProtoMappings by automatically calling :py:meth:`~mercator.ProtoMapping.to_protobuf`.
        """
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

    :param name_at_source: a string with the name of key or property to be extracted in an input object before casting into the target type.
    :param target_type: an optional :py:class:`~mercator.ProtoMapping` subclass or native python type. Check :ref:`target-type` for more details.
    """
    def cast(self, value):
        """
        :param value: a python object that is compatible with the given ``target_type``
        :returns: list of items target type coerced into the ``target_type``. Supports ProtoMappings by automatically calling :py:meth:`~mercator.ProtoMapping.to_protobuf`.
        """
        result = super().cast(value)

        if result is None:
            return

        if not isinstance(value, (list, tuple)):
            raise TypeCastError(f'ProtoList.cast() received a non-list value '
                                f'(type {type(value).__name__}): {value}')

        if issubclass(self.target_type, ProtoMapping):
            return [self.target_type(item).to_protobuf() for item in value]

        return [self.target_type(item) for item in value]


def extract_fields_from_dict(data: dict, names: dict):
    """Utility method used by :py:meth:`~mercator.ProtoMapping.to_dict`
    for extracting data plain python dictionaries.

    :param data: a dict with data to be mapped into protobuf objects
    :param names: a :py:class:`dict` with :py:class:`~mercator.meta.FieldMapping` for values.
    :returns: a dict with keyword-arguments to construct new protobuf messages.
    """
    return dict([(name, target.cast(data.get(target.name_at_source))) for name, target in names.items()])


def extract_fields_from_object(data: object, names: dict):
    """Utility method used by :py:meth:`~mercator.ProtoMapping.to_dict`
    for extracting data from instances of :ref:`source-input-type`.

    :param data: a dict with data to be mapped into protobuf objects
    :param names: a :py:class:`dict` with :py:class:`~mercator.meta.FieldMapping` for values.
    :returns: a dict with keyword-arguments to construct new protobuf messages.
    """
    return dict([(name, target.cast(getattr(data, target.name_at_source, None))) for name, target in names.items()])


class ProtoMapping(object, metaclass=MetaMapping):
    """Base class to define attribute mapping from :py:class:`dict` or
    :py:func:`~sqlalchemy.ext.declarative.declarative_base` subclasses'
    instances into pre-filled protobuf messages.

    Example:

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
        """
        :param data: a :py:class:`dict` or object compatible with the :ref:`source-input-type` declaration at the class level.
        """
        self.data = data

    def to_dict(self):
        """
        :returns: a :py:class:`dict` with keyword-arguments to construct a new instance of protobuf message defined by :ref:`proto`.
        """
        if self.data is None:
            return {}

        fields = self.__fields__
        if isinstance(self.data, dict):
            return extract_fields_from_dict(self.data, fields)

        elif isinstance(self.data, self.__source_input_type__):
            return extract_fields_from_object(self.data, fields)

        else:
            raise TypeError(f'{self.data} must be a dict or {self.__source_input_type__} but is {type(self.data)} instead')

    def to_protobuf(self):
        """
        :returns: a new :ref:`proto` instance with the data extracted with :py:meth:`~mercator.ProtoMapping.to_dict`.
        """
        data = self.to_dict()
        return self.__proto__(**data)
