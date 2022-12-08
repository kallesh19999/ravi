""""fix_removed_drplan_operator"

Revision ID: 965d03612833
Revises: 93dadf546197
Create Date: 2017-07-07 16:24:00.554392

"""
import json
import uuid
import string
import random
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, String, Integer, ForeignKey, TIMESTAMP,
                        TEXT, Boolean, and_, Index)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, Session
from alembic import op

from auth_server.utils import as_dict, ModelEncoder
from auth_server.models.exceptions import InvalidTreeException

# revision identifiers, used by Alembic.
revision = '965d03612833'
down_revision = '93dadf546197'
branch_labels = None
depends_on = None

def gen_id():
    return str(uuid.uuid4())


def gen_salt():
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(8))


class Base(object):
    @declared_attr
    # pylint: disable=E0213
    def __tablename__(cls):
        # pylint: disable=E1101
        return cls.__name__.lower()

    def to_dict(self):
        return as_dict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)


Base = declarative_base(cls=Base)


class BaseModel(object):
    created_at = Column(Integer, default=datetime.utcnow().timestamp,
                        nullable=False)
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0


class BaseMixin(BaseModel):
    id = Column(String(36), primary_key=True, default=gen_id)


class BaseIntKeyMixin(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)


class OrderMixin(object):
    order = Column(Integer, nullable=False, default=0)


class Type(Base, BaseIntKeyMixin):

    __tablename__ = 'type'

    parent_id = Column(Integer, ForeignKey('type.id'))
    name = Column(String(24), nullable=False, index=True, unique=True)
    assignable = Column(Boolean, nullable=False, default=True)
    children = relationship(
        'Type',
        # cascade deletions
        cascade="all",
        # many to one + adjacency list - remote_side
        # is required to reference the 'remote'
        # column in the join condition.
        backref=backref("parent", remote_side='Type.id'),
        # children will be represented as a dictionary
        # on the "name" attribute.
        collection_class=list)

    @hybrid_property
    def child_tree(self):
        all_ = []

        def get_childs(node, li):
            if node:
                list_element = node.children
                if len(list_element) == 1:
                    li.append(list_element[0])
                    get_childs(list_element[0], li)
                elif len(list_element) > 1:
                    raise InvalidTreeException("Invalid tree format")
            else:
                return

        get_childs(self, all_)
        return sorted(all_, key=lambda x: x.id)

    @hybrid_property
    def parent_tree(self):
        all_ = []

        def get_parents(node, li):
            if node:
                element = node.parent
                if element:
                    li.append(element)
                    get_parents(element, li)
            else:
                return

        get_parents(self, all_)
        return sorted(all_, key=lambda x: x.id, reverse=True)

    def __init__(self, id=None, name=None, parent=None, assignable=True):
        self.id = id
        self.name = name
        self.parent = parent
        self.assignable = assignable

    def append(self, node_name):
        self.children[node_name] = Type(node_name, parent=self)

    def __repr__(self):
        return "Type(name=%r, id=%r, parent_id=%r)" % (self.name, self.id,
                                                       self.parent_id)


class User(Base, BaseMixin):

    __tablename__ = 'user'

    display_name = Column(String(64), nullable=False, index=False)
    is_active = Column(Boolean, nullable=False, default=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password = Column(String(64), nullable=False)
    salt = Column(String(20), nullable=False)
    scope_id = Column(String(36), index=True, nullable=True)
    type = relationship("Type", backref="users")

    def to_dict(self):
        user_dict = as_dict(self)
        return dict(filter(
            lambda x: x[0] not in [User.salt.name, User.password.name],
            user_dict.items()))

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)

    def __init__(self, email=None, type=None, password=None,
                 salt=None, scope_id=None, type_id=None, display_name=None,
                 is_active=True):
        if type:
            self.type = type
        if type_id is not None:
            self.type_id = type_id
        self.email = email
        self.password = password
        self.salt = salt if salt else gen_salt()
        self.scope_id = scope_id
        self.is_active = is_active
        self.display_name = display_name
        self.roles = []

    def __repr__(self):
        return '<User %s>' % self.email


class Token(Base):

    __tablename__ = 'token'

    token = Column(String(350), primary_key=True, nullable=False)
    user_id = Column(String(36), ForeignKey('user.id'))
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    valid_until = Column(TIMESTAMP, nullable=False, index=True)
    ip = Column(String(39), nullable=False)
    user = relationship("User", backref="tokens")


class Role(Base, BaseIntKeyMixin):

    __tablename__ = 'role'

    name = Column(String(64), index=True, nullable=False)
    description = Column(TEXT, nullable=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    lvl_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    scope_id = Column(String(36), nullable=True)
    shared = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    actions = relationship("Action", secondary="role_action")
    type = relationship("Type", backref="roles", foreign_keys=[type_id])
    lvl = relationship("Type", backref="levels", foreign_keys=[lvl_id])
    __table_args__ = (Index('idx_role_name_scope', "name", "type_id",
                            "scope_id", unique=True),)

    def assign_action(self, action):
        self.role_action.append(RoleAction(role=self, action=action))

    def remove_action(self, action):
        self.actions.remove(action)

    def __init__(self, name=None, type=None, lvl=None, shared=False,
                 is_active=True, scope_id=None, description=None, type_id=None,
                 lvl_id=None):
        if type:
            self.type = type
        if type_id is not None:
            self.type_id = type_id
        if lvl:
            self.lvl = lvl
        if lvl_id is not None:
            self.lvl_id = lvl_id
        self.name = name
        self.scope_id = scope_id
        self.shared = shared
        self.is_active = is_active
        self.description = description
        self.users = []

    def __repr__(self):
        return '<Role %s (type: %s) >' % (self.name, self.type.name)


class Action(BaseIntKeyMixin, Base, OrderMixin):

    __tablename__ = 'action'

    name = Column(String(64), index=True, nullable=False, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'))
    action_group_id = Column(Integer, ForeignKey('action_group.id'),
                             nullable=False)
    action_group = relationship("ActionGroup", backref="actions")
    type = relationship("Type", backref='actions')
    roles = relationship("Role", secondary="role_action", viewonly=True)

    def __init__(self, name=None, type=None, action_group=None,
                 action_group_id=None, order=0):
        if action_group:
            self.action_group = action_group
        if action_group_id is not None:
            self.action_group_id = action_group_id
        self.name = name
        self.type = type
        self.order = order
        self.roles = []

    def __repr__(self):
        return '<Action %s>' % self.name


class ActionGroup(BaseIntKeyMixin, Base, OrderMixin):

    __tablename__ = 'action_group'

    name = Column(String(24), index=True, nullable=False, unique=True)

    def __init__(self, name=None, order=0):
        self.name = name
        self.order = order

    @property
    def actual_actions(self):
        return Session.object_session(self).query(Action).filter(
            and_(
                Action.deleted.is_(False),
                Action.action_group_id == self.id
            )
        ).all()

    def __repr__(self):
        return '<ActionGroup %s>' % self.name


class RoleAction(Base):

    __tablename__ = 'role_action'

    id = Column(String(36), default=gen_id, primary_key=True, unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)
    action_id = Column(Integer, ForeignKey('action.id'), primary_key=True)

    role = relationship("Role", backref=backref(
        "role_action", cascade="all, delete-orphan"))
    action = relationship("Action", backref=backref(
        "role_action", cascade="all, delete-orphan"))

    def __init__(self, role=None, action=None):
        self.id = gen_id()
        self.role = role
        self.action = action

    def __repr__(self):
        return '<RoleAction {}>'.format(self.role.name + " " +
                                        self.action.name)


class Assignment(Base, BaseMixin):

    __tablename__ = 'assignment'

    id = Column(String(36), default=gen_id, primary_key=True, unique=True)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False)
    resource_id = Column(String(36), index=True, nullable=True)
    user = relationship("User", backref='assignments')
    role = relationship("Role", backref='assignments')
    type = relationship("Type", backref='assignments')

    def __init__(self, user=None, role=None, type=None, resource_id=None,
                 role_id=None):
        self.user = user
        if role:
            self.role = role
        if role_id is not None:
            self.role_id = role_id
        self.type = type
        self.resource_id = resource_id

    def __repr__(self):
        return '<Assignment type: %s user: %s role: %s resource: %s>' % (
            self.type.name, self.user.email, self.role.name, self.resource_id)


def upgrade():

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_customer = session.query(Type).filter_by(
                name='customer').one_or_none()
        role_drplan_operator = session.query(Role).filter_by(
            name='Drplan Operator',
            type_id=type_customer.id,
            scope_id=None).one_or_none()
        if role_drplan_operator:
            for action in role_drplan_operator.actions:
                role_drplan_operator.remove_action(action)
        role_drplan_operator.deleted_at = datetime.utcnow().timestamp()
        session.add(role_drplan_operator)
        session.commit()
    finally:
        session.close()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        type_customer = session.query(Type).filter_by(
            name='customer').one_or_none()
        role_drplan_operator = session.query(Role).filter_by(
            name='Drplan Operator',
            type_id=type_customer.id,
            scope_id=None).one_or_none()
        role_drplan_operator.deleted_at = 0
        session.add(role_drplan_operator)
        session.commit()
    finally:
        session.close()
