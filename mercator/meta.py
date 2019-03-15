import inspect
from .errors import ProtobufCastError
from google.protobuf.descriptor import FieldDescriptor

REGISTRY = {}
BASE_MODEL_CLASS_REGISTRY = {}


class MercatorDomainClass(object):
    """The existence of this class is a trick to avoid redundant imports.

    Any subclasses of this are automatically supported by
    :py:class:`~mercator.meta.FieldMapping` as ``target_type``.

    This was introduced to support
    :py:class:`~mercator.SinglePropertyMapping` but can be used in the
    future in any new types that leverage type casting.
    """


class FieldMapping(object):
    """Base-class for field mapping declaration in :py:class:`~mercator.ProtoMapping`
    that is:

    - :py:class:`~mercator.ProtoKey`
    - :py:class:`~mercator.ProtoList`

    This base-class resides in :py:mod:`mercator.meta`
    so the metaclass can capture the field mapping declarations during
    import-time.

    :param name_at_source: a string with the name of key or property to be extracted in an input object before casting into the target type.
    :param target_type: an optional :py:class:`~mercator.ProtoMapping` subclass or native python type. Check :ref:`target-type` for more details.
    """
    def __init__(self, name_at_source: str, target_type: type = None):
        self.name_at_source = name_at_source
        self.target_type = target_type

        if target_type is not None and not isinstance(target_type, type) and not isinstance(target_type, MercatorDomainClass):
            raise TypeError(f'{self.__class__} takes a type as second argument, but got {type(target_type).__name__} instead')

    def cast(self, value):
        """coerces the given ``value`` into the target type.
        :param value: a python object that is compatible with the given ``target_type``
        """
        if value is None:
            return

        if self.target_type is None:
            return value

        try:
            return self.target_type(value)
        except (ValueError, TypeError) as e:
            msg = str(e)
            raise ProtobufCastError(f'{msg} while casting "{value}" ({type(value).__name__}) to {self.target_type.__name__}')


class ImplicitField(FieldMapping):
    """Like :py:class:`~mercator.ProtoKey` but works is
    declared automagically by the metaclass.
    """


def is_field_property(obj):
    """utility function to check if the give object is a field from a protobuf message.

    For now there is not much metadata when inspecting a protobuf
    class compiled by protoc, so the current strategy is:

    1. Take the ``obj.__class__``
    2. Take the ``__name__`` of the class.
    3. Check that the name contains the string "FieldProperty"

    """
    cls = getattr(obj, '__class__', None)
    name = getattr(cls, '__name__', '')
    return name and 'FieldProperty' in name


def field_properties_from_proto_class(proto_class):
    """inspects all members of the given proto_class and returns a list of
    those who seem to be a message field (determined by :py:meth:`~mercator.meta.is_field_property`)
    """
    members = inspect.getmembers(proto_class)
    return [k for k, v in members if is_field_property(v)]


def validate_proto_attribute(name, attributes):
    """Invoked by :py:class:`~mercator.MetaMapping` during "import time"
    to validate the declaration of :ref:`proto`.
    """
    proto_cls = attributes.get('__proto__')
    if not proto_cls:
        raise SyntaxError(f'class {name} does not define a __proto__')

    return proto_cls

def validate_and_register_base_model_class(cls, name, attributes):
    """Invoked by :py:class:`~mercator.MetaMapping` during "import time"
    to validate the declaration of :ref:`source-input-type`.
    """
    base_model_class = attributes.get('__source_input_type__')
    if not base_model_class:
        return

    if not isinstance(base_model_class, type):
        raise SyntaxError(f'class {name} defined a __source_input_type__ attribute that is not a valid python type: {base_model_class}')
    else:
        BASE_MODEL_CLASS_REGISTRY[base_model_class] = cls


class MetaMapping(type):
    """Metaclass to leverage and enforce correct syntax sugar when
    declaring protomappings.

    Check the source code for comments explaining how everything
    works.
    """
    def __new__(cls, name, bases, attributes):
        cls = type.__new__(cls, name, bases, attributes)
        if name in ('MetaMapping', 'ProtoMapping'):
            return cls

        proto_cls = validate_proto_attribute(name, attributes)
        validate_and_register_base_model_class(cls, name, attributes)

        # extract field names from the __proto__ class, those will
        # become "ImplicitField" instances in the eyes of mercator.
        field_names = field_properties_from_proto_class(proto_cls)

        # create a dictionary with all default implicit fields
        implicit_field_mappings = dict([(k, ImplicitField(k)) for k in field_names])

        # extract all FieldMapping declarations from the ProtoMapping
        # itself, this means all ProtoKey and ProtoList arguments will
        # be considered "explicit fields" in the eyes of mercator.
        explicit_field_mappings = dict([(k, v) for k, v in attributes.items() if isinstance(v, FieldMapping)])

        # store the metadata in the class definition to leverage the
        # whole magic of mapping attributes.
        cls.__field_names__ = field_names
        cls.__implicit_mappings__ = implicit_field_mappings
        cls.__explicit_mappings__ = explicit_field_mappings

        # generate one final dict with the implicit and explicit fields.
        # note the deliberate override of  implicit fields with explicit ones.
        cls.__fields__ = dict(list(implicit_field_mappings.items()) + list(explicit_field_mappings.items()))

        # register all ProtoMapping declarations collected during
        # "import time" in a global dictionary that can be used for
        # instrospection and debugging of existing mappings.
        REGISTRY[name] = cls

        return cls
