import inspect
from .errors import ProtobufCastError

REGISTRY = {}
BASE_MODEL_CLASS_REGISTRY = {}


class MercatorDomainClass(object):
    pass


class FieldMapping(object):
    """Base-class for field mapping declaration in :py:class:`~shared.grpc.protomapper.ProtoMapping`
    that is:

    - :py:class:`~shared.grpc.protomapper.ProtoKey`
    - :py:class:`~shared.grpc.protomapper.ProtoList`


    This base-class resides in :py:mod:`shared.grpc.protomapper.meta`
    so the metaclass can capture the field mapping declarations during
    import-time.
    """
    def __init__(self, name_at_source:str, target_type:type=None):
        self.name_at_source = name_at_source
        self.target_type = target_type

        if target_type is not None and not isinstance(target_type, type) and not isinstance(target_type, MercatorDomainClass):
            raise TypeError(f'{self.__class__} takes a type as second argument, but got {type(target_type).__name__} instead')

    def cast(self, value):
        if value is None:
            return

        if self.target_type is None:
            return value

        try:
            return self.target_type(value)
        except (ValueError, TypeError) as e:
            msg = str(e)
            raise ProtobufCastError(f'{msg} while casting "{value}" ({type(value).__name__}) to {self.target_type.__name__}')


class ImplicitMapping(FieldMapping):
    """Like :py:class:`~shared.grpc.protomapper.ProtoKey` but works is
    declared automagically by the metaclass.
    """


def is_field_property(obj):
    cls = getattr(obj, '__class__', None)
    name = getattr(cls, '__name__', '')
    return name and 'FieldProperty' in name


def field_properties_from_proto_class(proto_class):
    members = inspect.getmembers(proto_class)
    return [k for k, v in members if is_field_property(v)]


class MetaMapping(type):
    def __new__(cls, name, bases, attributes):
        cls = type.__new__(cls, name, bases, attributes)
        if name not in ('MetaMapping', 'ProtoMapping'):
            proto_cls = attributes.get('__proto__')
            if not proto_cls:
                raise SyntaxError(f'class {name} does not define a __proto__')

            base_model_class = attributes.get('BaseModelClass')
            if base_model_class:
                if not isinstance(base_model_class, type):
                    raise SyntaxError(f'class {name} defined a BaseModelClass attribute that is not a valid python type: {base_model_class}')

                BASE_MODEL_CLASS_REGISTRY[base_model_class] = cls

            field_names = field_properties_from_proto_class(proto_cls)
            implicit_field_mappings = dict([(k, ImplicitMapping(k)) for k in field_names])
            explicit_field_mappings = dict([(k, v) for k, v in attributes.items() if isinstance(v, FieldMapping)])

            cls.__field_names__ = field_names
            cls.__implicit_mappings__ = implicit_field_mappings
            cls.__explicit_mappings__ = explicit_field_mappings
            cls.__fields__ = dict(list(implicit_field_mappings.items()) + list(explicit_field_mappings.items()))

            REGISTRY[name] = cls

        return cls
