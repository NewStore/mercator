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


def test_proto_list_native_type():
    "ProtoList() should return a list of native types"

    field = ProtoList('user_ids', str)
    result = field.cast([1, 2])

    result.should.be.a(list)
    result.should.have.length_of(2)
    result.should.equal(['1', '2'])

    t1, t2 = result
    t1.should.be.a(str)
    t2.should.be.a(str)


def test_proto_list_int_type():
    "ProtoList() should return a list of integers if target_type is int"

    field = ProtoList('user_ids', int)
    result = field.cast(['1', 2])

    result.should.be.a(list)
    result.should.have.length_of(2)
    result.should.equal([1, 2])

    t1, t2 = result
    t1.should.be.a(int)
    t2.should.be.a(int)


def test_proto_list_with_target_type_none():
    "ProtoList() cast should return an origin value if target_type is None"
    field = ProtoList('user_ids')
    result = field.cast(['1', 2])

    result.should.be.a(list)
    result.should.have.length_of(2)
    result.should.equal(['1', 2])


def test_proto_list_with_target_type_none_and_non_list_tuple():
    "ProtoList() should raise an error if target_type is None and not fed with a list or tuple"

    field = ProtoList('tokens')
    when_called = field.cast.when.called_with('some tokens as string')

    when_called.should.have.raised(TypeCastError)
