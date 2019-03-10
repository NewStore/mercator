# -*- coding: utf-8 -*-
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base


BaseModel = declarative_base()


def PrimaryKeyUUID():
    return sa.Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )


class User(BaseModel):
    __tablename__ = 'user'
    __table_args__ = {'useexisting': True}

    uuid = PrimaryKeyUUID()
    login = sa.Column(sa.String(256))
    email = sa.Column(sa.String(256))
    password = sa.Column(sa.String(256))
    extra_info = sa.Column(
        postgresql.JSON,
        nullable=True,
    )


class AuthToken(BaseModel):
    __tablename__ = 'auth_token'
    __table_args__ = {'useexisting': True}

    uuid = PrimaryKeyUUID()
    data = sa.Column(sa.String(256))
    created_at = sa.Column(sa.Integer)
    owner_id = sa.Column(
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey('User.uuid')
    )
    owner = sa_orm.relationship(
        User,
        primaryjoin='and_(User.uuid == foreign(AuthToken.owner_id))',
        backref='tokens',
        uselist=False,
    )


class Media(BaseModel):
    __tablename__ = 'media'
    __table_args__ = {'useexisting': True}

    uuid = PrimaryKeyUUID()
    author_id = sa.Column(
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey('User.uuid')
    )
    author = sa_orm.relationship(
        User,
        primaryjoin='and_(Media.author_id == foreign(User.uuid))',
        backref='media',
        uselist=False,
    )
    url = sa.Column(sa.String(256))
