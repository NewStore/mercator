# -*- coding: utf-8 -*-
from uuid import uuid4
from .mappings import (
    UserMapping,
    MediaMapping,
)

from . import domain_pb2
from . import sql


def test_mapping_simple_1to1_from_sqlalchemy_object():
    ("ProtoMapping should be smart enough to infer fields "
     "from protobuf and extract data from a model")

    # Given a  instance
    sql_user = sql.User(
        login='Hulk',
        email='bruce@avengers.world',
    )

    # When I convert to protobuf
    user = UserMapping(sql_user).to_protobuf()

    # Then it should return an instance of my protobuf type
    user.should.be.an(domain_pb2.User)
    user.should.have.property('username').being.equal('Hulk')
    user.should.have.property('email').being.equal('bruce@avengers.world')


def test_mapping_of_mappings():
    ("ProtoMapping should use support nested mappings for nested model data")

    # Given a full dictionary with auth response data
    user = sql.User(
        uuid=uuid4(),
        login='chucknorris',
    )
    sql_media = sql.Media(
        url='https://test.com/media/123/download',
        author_id=user.uuid,
        author=user,
    )

    # When I convert to protobuf
    data = MediaMapping(sql_media).to_protobuf()

    # Then it should have its opaque properties
    data.should.have.property('author')
    data.should.have.property('download_url').being.equal('')
    data.author.should.have.property('username').being.equal('chucknorris')
