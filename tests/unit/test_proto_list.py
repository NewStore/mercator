# -*- coding: utf-8 -*-
from google.protobuf.timestamp_pb2 import Timestamp

from mercator import ProtoList, ProtoKey, ProtoMapping
from mercator.errors import TypeCastError


class TimestampMapping(ProtoMapping):
    __proto__ = Timestamp

    seconds = ProtoKey('seconds', int)


def test_proto_list_from_none():
    "ProtoList() should return None if input value is None"

    field = ProtoList('tokens', TimestampMapping)
    result = field.cast(None)

    result.should.be.none


def test_proto_list_proto_mapping():
    "ProtoList() should return a list of messages when target type is a ProtoMapping"

    field = ProtoList('tokens', TimestampMapping)
    result = field.cast([
        {
            'seconds': 1552263384
        },
        {
            'seconds': 1552263884
        },
    ])

    result.should.be.a(list)
    result.should.have.length_of(2)

    t1, t2 = result
    t1.should.be.a(Timestamp)
    t2.should.be.a(Timestamp)

    t1.seconds.should.equal(1552263384)
    t2.seconds.should.equal(1552263884)


def test_proto_list_non_list_tuple():
    "ProtoList() should raise an error if not fed with a list or tuple"

    field = ProtoList('tokens', TimestampMapping)
    when_called = field.cast.when.called_with('some tokens as string')

    when_called.should.have.raised(TypeCastError)
