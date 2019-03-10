class TypeCastError(Exception):
    """Raised when trying to cast a value of the wrong type.
    Used primarily by :py:meth:`~shared.grpc.protomapper.ProtoList.cast` from :py:class:`~shared.grpc.protomapper.ProtoList`
    """


class ProtobufCastError(Exception):
    """raised when failed to create a :py:class:`~google.protobuf.message.Message` instance
    """
