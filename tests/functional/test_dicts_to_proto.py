# -*- coding: utf-8 -*-
from .mappings import (
    UserMapping,
    AuthRequestMapping,
    AuthResponseMapping,
)

from . import domain_pb2


def test_mapping_simple_1to1_from_dict():
    ("ProtoMapping should be smart enough to infer fields "
     "from protobuf and extract data from a dictionary")
    # Given a dict with user data
    info = {
        'login': 'Hulk',
        'email': 'bruce@avengers.world',
        'tokens': [
            {
                'data': 'this is the token',
                'created_at': 1552240433,
                'expires_at': 1552240733,
            }
        ],
        # 'extra_info': {
        #     'just': 'some',
        #     'arbitrary': 'json data',
        # }
    }

    # When I convert to protobuf
    user = UserMapping(info).to_protobuf()

    # Then it should return an instance of my protobuf type
    user.should.be.an(domain_pb2.User)
    user.should.have.property('username').being.equal('Hulk')
    user.should.have.property('email').being.equal('bruce@avengers.world')
    user.should.have.property('tokens').being.length_of(1)
    user.should.have.property('metadata')


def test_mapping_specific_fields():
    ("ProtoMapping should rename specified ProtoKey fields")

    # Given a dict with auth request data
    request = {
        'username': 'Hulk',
        'password': 'H00LK5m4sh',
    }

    # When I convert to protobuf
    data = AuthRequestMapping(request).to_protobuf()

    # Then it should have returned a protobuf
    data.should.be.an(domain_pb2.AuthRequest)

    # And it should have mapped the specific field appropriately
    data.should.have.property('username').being.equal('Hulk')
    data.should.have.property('password').being.equal('H00LK5m4sh')


def test_mapping_of_mappings():
    ("ProtoMapping should use support nested mappings for nested dict data")

    # Given a full dictionary with auth response data
    token_data = {
        'token': {
            'data': 'this is the token',
            'created_at': 1552240433,
            'expires_at': 1552240733,
        }
    }

    # When I convert to protobuf
    data = AuthResponseMapping(token_data).to_protobuf()

    # Then it should have its opaque properties
    data.should.have.property('token')
    data.token.should.have.property('value').being.equal('this is the token')
