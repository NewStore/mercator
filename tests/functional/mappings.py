import grpc
from concurrent.futures import ThreadPoolExecutor

from mercator import (
    ProtoMapping,
    ProtoKey,
    ProtoList,
    SinglePropertyMapping,
)
from google.protobuf.timestamp_pb2 import Timestamp

from . import domain_pb2
from . import domain_pb2_grpc
from . import sql

ProtobufTimestamp = SinglePropertyMapping(int, Timestamp, 'seconds')


class AuthRequestMapping(ProtoMapping):
    __proto__ = domain_pb2.AuthRequest

    username = ProtoKey('username', str)
    password = ProtoKey('password', str)


class UserAuthTokenMapping(ProtoMapping):
    __proto__ = domain_pb2.User.AuthToken
    __source_input_type__ = sql.AuthToken
    value = ProtoKey('data', str)
    created_at = ProtoKey('created_at', ProtobufTimestamp)
    expires_at = ProtoKey('expires_at', ProtobufTimestamp)


class UserMapping(ProtoMapping):
    __proto__ = domain_pb2.User
    __source_input_type__ = sql.User

    uuid = ProtoKey('id', str)
    email = ProtoKey('email', str)
    username = ProtoKey('login', str)
    tokens = ProtoList('tokens', UserAuthTokenMapping)
    metadata = ProtoKey('extra_info', dict)


class MediaMapping(ProtoMapping):
    __proto__ = domain_pb2.UserMedia

    __source_input_type__ = sql.Media
    author = ProtoKey('author', UserMapping)
    download_url = ProtoKey('link', str)
    blob = ProtoKey('blob', bytes)
    content_type = ProtoKey('content_type', bytes)


class AuthResponseMapping(ProtoMapping):
    __proto__ = domain_pb2.AuthResponse

    token = ProtoKey('token', UserAuthTokenMapping)


class MediaRequestMapping(ProtoMapping):
    __proto__ = domain_pb2.MediaRequest


class MediaServicer(domain_pb2_grpc.MediaServicer):
    def GetMedia(self, request, context):
        media = business_logic_module.retrieve_media_from_sqlalchemy(
            uuid=request.media_uuid,
            name=request.media_name,
        )

        return MediaMapping(media).to_protobuf()


server = grpc.server(
    ThreadPoolExecutor(max_workers=10)
)
domain_pb2_grpc.add_MediaServicer_to_server(MediaServicer(), server)
