from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declared_attr, declarative_base, as_declarative


Base = declarative_base()


@as_declarative()
class Base:
    # 生成表名，不包含 'Base' 后缀
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() if cls.__name__ != 'Base' else ''

    # 定义共享字段
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    created_by = sa.Column(sa.String(255), nullable=False)
    updated_by = sa.Column(sa.String(255), nullable=False)


class Award(Base):
    """ 奖品表 """
    __tablename__ = 'award'
    room_id = sa.Column(sa.String(128))
    # 奖品名
    name = sa.Column(sa.String(255))
    # 奖品状态
    status = sa.Column(sa.Integer)
    # 发起人
    promoter = sa.Column(sa.String(128))
    # 获奖人
    winner = sa.Column(sa.String(512))
    # 备注
    remark = sa.Column(sa.Text)


class ChatHistory(Base):
    __tablename__ = 'chat_history'
    name = sa.Column(sa.String(128))
    wxid = sa.Column(sa.String(128))
    room_id = sa.Column(sa.String(128))
    room_name = sa.Column(sa.String(128))
    # 记录内容
    content = sa.Column(sa.Text)
    # 消息id
    msg_id = sa.Column(sa.BigInteger)
    # 消息类型
    type = sa.Column(sa.Integer)
    # 消息xml
    xml = sa.Column(sa.Text)


class GroupMember(Base):
    __tablename__ = 'group_member'
    wxid = sa.Column(sa.String(128))
    room_id = sa.Column(sa.String(128))
    room_name = sa.Column(sa.String(128))
    # 群聊名
    name = sa.Column(sa.String(128))
    # 加入类型
    join_type = sa.Column(sa.Integer)
    # 是否已经离开
    is_leave = sa.Column(sa.Boolean)
    # 是否是 管理员
    is_admin = sa.Column(sa.Boolean)


class NameHistory(Base):
    __tablename__ = 'name_history'
    wxid = sa.Column(sa.String(128))
    room_id = sa.Column(sa.String(128))
    # 原名称
    old_name = sa.Column(sa.String(128))
    # 新名称
    new_name = sa.Column(sa.String(128))


class Raffle(Base):
    __tablename__ = 'raffle'
    wxid = sa.Column(sa.String(128))
    room_id = sa.Column(sa.String(128))
    # 状态
    status = sa.Column(sa.Integer)
    # 权重
    weight = sa.Column(sa.Integer)
    # 奖品名
    award_name = sa.Column(sa.String(128))
    # 奖品id
    award_id = sa.Column(sa.Integer)


class UserAt(Base):
    __tablename__ = 'user_at'
    wxid = sa.Column(sa.String(128))
    room_id = sa.Column(sa.String(128))
    # at全体内容
    at_content = sa.Column(sa.Text)


class GameName(Base):

    __tablename__ = 'game_name'
    room_id = sa.Column(sa.String(128))
    wxid = sa.Column(sa.String(128))
    # 冒险团名
    team_name = sa.Column(sa.String(128))
    # 其他角色名
    other_names = sa.Column(sa.String(128))


