# -*- coding: utf-8 -*-
from mercator.meta import FieldMapping


def test_proto_key_invalid_type():
    "FieldMapping() should raise TypeError if the target_type argument is not a type"

    when_called = FieldMapping.when.called_with(
        'some_name',
        'this_is_not_a_type',
    )

    when_called.should.have.raised(
        TypeError,
        "<class 'mercator.meta.FieldMapping'> takes a type as second argument, but got str instead"
    )
