# -*- coding: utf-8 -*-
from mercator import ProtoKey


def test_field_mapping_cast_returns_doesnt_touch_value_target_type_none():
    "FieldMapping.cast() returns the value untouched if the target type is None"

    key = ProtoKey('username')

    value = object()

    result = key.cast(value)

    result.should.equal(value)
