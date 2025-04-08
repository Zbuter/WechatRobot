from enum import Enum


class AwardStatus(Enum):
    Padding = 0
    Finish = 1
    Deleted = 2
class RaffleStatus(Enum):
    Add = 0
    Delete = 1

class SendMessageType(Enum):
    Text = 0
    File = 1
    Image = 2
    Emotion = 3
    Pat = 4
    RichText = 5


class GroupMemberJoinType(Enum):
    SystemSync = 0
    Invite = 1,
    Game = 2,
    Scan = 3,


class WechatMessageType(Enum):
    Moment = 0
    Text = 1
    Image = 3
    Voice = 34
    VerifyMsg = 37
    PossibleFriendMsg = 40
    ShareCard = 42
    Video = 43
    Emoticon = 47
    Location = 48
    App = 49
    VoipMsg = 50
    StatusNotify = 51
    VoipNotify = 52
    VoipInvite = 53

    # 引用消息
    ReferMsg = 54

    MicroVideo = 62
    VerifyMsgEnterprise = 65
    Transfer = 2000  # 转账
    RedEnvelope = 2001  # 红包
    MiniProgram = 2002  #小程序
    GroupInvite = 2003  # 群邀请
    File = 2004  #文件消息
    SysNotice = 9999
    Sys = 10000
    Recalled = 10002  # NOTIFY   服务通知


def get_enum_by_value(enum_cls, value):
    """
    根据值查找枚举成员名
    """
    for member in enum_cls:
        if member.value == value:
            return member
    return None
