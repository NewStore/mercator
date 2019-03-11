# -*- coding: utf-8 -*-
from google.protobuf.timestamp_pb2 import Timestamp

from mercator import ProtoKey, ProtoMapping
from mercator.errors import ProtobufCastError


class TimestampMapping(ProtoMapping):
    __proto__ = Timestamp

    seconds = ProtoKey('seconds', int)


def test_proto_mapping_from_none():
    "ProtoMapping() should return None if input value is of invalid type"

    mapping = TimestampMapping({'seconds': {'invalid': 'val'}})

    when_called = mapping.to_protobuf.when.called

    when_called.should.have.raised(
        ProtobufCastError,
        'int() argument must be a string, a bytes-like object or a number, not \'dict\' while casting "{\'invalid\': \'val\'}" (dict) to int'
    )
