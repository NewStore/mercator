class TypeCastError(Exception):
    """Raised when trying to cast a value of the wrong type.
    Used primarily by :py:meth:`mercator.ProtoList.cast` from :py:class:`~mercator.ProtoList`
    """


class ProtobufCastError(Exception):
    """raised when failed to create a :py:class:`~google.protobuf.message.Message` instance
    """
