# -*- coding: utf-8 -*-
from google.protobuf.timestamp_pb2 import Timestamp

from mercator import ProtoKey, ProtoMapping
from mercator.errors import ProtobufCastError


class MyCustomObjectWithTimestampData:
    """this class is used as input for tests where proto mappings declare
    __source_input_type__.
    """
    def __init__(self, seconds):
        self.seconds = seconds


class TimestampMapping(ProtoMapping):
    __proto__ = Timestamp
    __source_input_type__ = MyCustomObjectWithTimestampData
    seconds = ProtoKey('seconds', int)


def test_proto_mapping_from_none():
    "ProtoMapping() should return None if input value is of invalid type"

    mapping = TimestampMapping({'seconds': {'invalid': 'val'}})

    when_called = mapping.to_protobuf.when.called

    when_called.should.have.raised(
        ProtobufCastError,
        'int() argument must be a string, a bytes-like object or a number, not \'dict\' while casting "{\'invalid\': \'val\'}" (dict) to int'
    )


def test_proto_mapping_to_dict_when_none():
    "ProtoMapping() should return empty dict if input value None"

    mapping = TimestampMapping(None)

    result = mapping.to_dict()

    result.should.be.a(dict)
    result.should.equal({})


def test_proto_mapping_to_dict_when_none():
    "ProtoMapping() should return empty dict if input value None"

    mapping = TimestampMapping(None)

    result = mapping.to_dict()

    result.should.be.a(dict)
    result.should.equal({})
