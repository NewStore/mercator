# -*- coding: utf-8 -*-
from mock import patch
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


def test_proto_mapping_from_invalid():
    "ProtoMapping.to_protobuf() should raise exception if input value is invalid"

    mapping = TimestampMapping({'seconds': {'invalid': 'val'}})

    when_called = mapping.to_protobuf.when.called

    when_called.should.have.raised(
        ProtobufCastError,
        'int() argument must be a string, a bytes-like object or a number, not \'dict\' while casting "{\'invalid\': \'val\'}" (dict) to int'
    )


def test_proto_mapping_to_dict_when_none():
    "ProtoMapping.to_dict() should return empty dict if input value None"

    mapping = TimestampMapping(None)

    result = mapping.to_dict()

    result.should.be.a(dict)
    result.should.equal({})


def test_proto_mapping_object_incompatible_with_source_input_type():
    "ProtoMapping.to_dict() should raise TypeError if the input object is not a subclass of __source_input_type__"

    class DummyObject:
        def __repr__(self):
            return '<dummy_object>'

    dummy_object = DummyObject()

    mapping = TimestampMapping(dummy_object)

    when_called = mapping.to_dict.when.called

    when_called.should.have.raised(
        TypeError,
        "<dummy_object> must be a dict "
        "or <class 'tests.unit.test_proto_mapping.MyCustomObjectWithTimestampData'> "
        "but is <class 'tests.unit.test_proto_mapping.test_proto_mapping_object_incompatible_with_source_input_type.<locals>.DummyObject'> instead")
