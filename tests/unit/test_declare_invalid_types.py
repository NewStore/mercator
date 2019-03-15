# -*- coding: utf-8 -*-
from google.protobuf.message import Message

from mercator import ProtoMapping


def test_declare_mapping_missing_proto():
    "SyntaxError should be raised when declaring a proto mapping without a __proto__ attribute"

    def declare_invalid():
        class Foo(ProtoMapping):
            pass

    declare_invalid.when.called.should.have.raised(
        SyntaxError,
        'class Foo does not define a __proto__'
    )


def test_declare_mapping_invalid_base_model_class():
    "SyntaxError should be raised when declaring a proto mapping with __source_input_type__ that is not a type"

    def declare_invalid():
        class Foo(ProtoMapping):
            __proto__ = Message
            __source_input_type__ = 'foobar'

    declare_invalid.when.called.should.have.raised(
        SyntaxError,
        'class Foo defined a __source_input_type__ attribute that is not a valid python type: foobar'
    )
