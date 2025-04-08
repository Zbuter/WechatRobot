# -*- coding: utf-8 -*-

import logging
import os
import re
import signal
import time
from pathlib import Path
from queue import Empty
from threading import Thread
from typing import Dict, List
import xml.etree.ElementTree as ET

import requests
from wcferry import Wcf, WxMsg

from wechat_robot.enums import SendMessageType, WechatMessageType, GroupMemberJoinType
from wechat_robot.exceptions import RobotSendMessageException
from wechat_robot.models import *

__version__ = "39.4.2.2"

from wechat_robot.utils import DatabaseManager
from wechat_robot.job_mgmt import Job
from wechat_robot.plugin_loader import PluginLoader

from wechat_robot.config import Config


class Robot(Job):
    db: DatabaseManager
    wcf: Wcf
    plugins = []

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.self_wxid = None
        self.member = None
        self.contacts = None
        self.plugin_loader = None
        self.LOG = logging.getLogger("Robot")
        self.config = config.robot_config
        self.storage_path = self.config['storage_path']
        self.db = DatabaseManager(self.config['database_url'])
        self.db_session = self.db.session_scope

    def run(self):
        self.wcf = Wcf(host=self.config['rpc_wcf_addr'])
        self.self_wxid = self.wcf.get_self_wxid()
        self.plugin_loader = PluginLoader(self)
        os.path.abspath(os.path.dirname(__file__))
        self.plugin_loader.load_plugins(f"{os.path.abspath(os.path.dirname(__file__)) + os.sep}plugins")
        self.plugin_loader.call_init_methods()
        self.member = {}
        self.contacts = []
        signal.signal(signal.SIGINT, self.cleanup)
        self.enableReceivingMsg()  # 加队列
        self.LOG.info(f"WeChatRobot【{__version__}】成功启动···")
        while True:
            self.runPendingJobs()
            time.sleep(1)

    def get_group_admin(self, room_id) -> List[GroupMember]:
        """ 获取 群 管理员"""
        with self.db_session() as db:
            return db.query(GroupMember).filter(GroupMember.room_id == room_id, GroupMember.is_admin == True).all()

    def is_group_admin(self, room_id: str, wxid: str) -> bool:
        """
        是否为管理员
        """
        admins = self.get_group_admin(room_id)
        for admin in admins:
            if admin.wxid == wxid:
                return True
        return False

    def get_mem_members(self, room_id) -> Dict | None:
        """获取群聊成员"""
        member = self.member.get(room_id)
        if member is None:
            self.refresh_mem_member(room_id)
            member = self.member.get(room_id)
        return member

    def get_contact(self, wxid: str):
        def get(wxid: str):
            if self.contacts is None:
                self.refresh_contact()

            for c in self.contacts:
                if c.get('wxid') == wxid:
                    return c

        contact = get(wxid)
        if contact is None:
            self.refresh_contact()
            contact = get(wxid)

        return contact

    def refresh_mem_member(self, room_id):
        """
        刷新内存中群成员
        """
        self.member[room_id] = self.wcf.get_chatroom_members(room_id)

    def refresh_contact(self):
        """
        刷新内存中联系人
        """
        self.contacts = self.wcf.get_contacts()

    def send_text(self, msg: str, receiver: str, at_list: str = "") -> None:
        """
        发送文本消息
        """
        self.send(SendMessageType.Text, receiver, msg, at_list=at_list)

    def send_file(self, path: str, receiver: str) -> None:
        """
        发送文件
        """
        self.send(SendMessageType.File, path, receiver)

    def send_image(self, path: str, receiver: str) -> None:
        """
        发送图片
        """
        self.send(SendMessageType.Image, path, receiver)

    def send_emotion(self, path, receiver) -> None:
        """
        发送表情
        """
        self.send(SendMessageType.Emotion, path, receiver)

    def send_pat(self, room_id, receiver) -> None:
        """
        拍一拍
        """
        self.send(SendMessageType.Pat, room_id, receiver)

    def send_rich_text(self, data, receiver) -> None:
        """
        发送链接
        """
        self.send_rich_text(data, receiver)

    def get_member_name(self, room_id: str, mem_wxid: str) -> str:
        """
        获取群成员的 群聊名
        """
        return self.get_mem_members(room_id).get(mem_wxid)

    def send(self, send_type: SendMessageType, receiver, data, **kwargs):
        """
        发送消息
        """
        at_list = kwargs.get("at_list", None)

        self.plugin_loader.handle_before_send_msg(data, receiver, **kwargs)

        def message(msg: str, rec: str, atlist: str = ""):
            """ 发送消息
               :param msg: 消息字符串
               :param rec: 接收人wxid或者群id
               :param atlist: 要@的wxid, @所有人的wxid为：notify@all
               """
            # msg 中需要有 @ 名单中一样数量的 @
            ats = ""
            if atlist:
                if atlist == "notify@all":  # @所有人
                    ats = " @所有人"
                else:
                    wxids = atlist.split(",")
                    for wxid in wxids:
                        # 根据 wxid 查找群昵称
                        ats += f" @{self.wcf.get_alias_in_chatroom(wxid, rec)}"

            # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三

            if ats == "":
                return self.wcf.send_text(f"{msg}", rec, at_list)
            else:
                return self.wcf.send_text(f"{ats}\n{msg}", rec, at_list)

        message_map = {
            SendMessageType.Text: lambda r, d, a: message(d, r, a),
            SendMessageType.File: lambda r, d, **kw: self.wcf.send_file(d, r),
            SendMessageType.Image: lambda r, d, **kw: self.wcf.send_image(d, r),
            SendMessageType.Emotion: lambda r, d, **kw: self.wcf.send_emotion(d, r),
            SendMessageType.Pat: lambda r, d, **kw: self.wcf.send_pat_msg(r, d),
            SendMessageType.RichText: lambda r, d, **kw: self.wcf.send_rich_text(
                d.get('name'),
                d.get('account'),
                d.get('title'),
                d.get('digest'),
                d.get('url'),
                d.get('thumburl'),
                r
            )
        }

        func = message_map.get(send_type, lambda r, d, **kw: None)
        ret = func(receiver, data, at_list)
        self.LOG.info(f"To {receiver}:[{send_type}]: {data} ")

        if ret != 0:
            raise RobotSendMessageException(f"Failed to send [{send_type}]: {data} \n receiver: {receiver}")

        self.plugin_loader.handle_after_send_msg(data, receiver, **kwargs)

    def can_download(self, msg: WxMsg) -> bool:
        """ 是否可下载 """
        # return msg.type in [WechatMessageType.Image.value, WechatMessageType.Emoticon.value,
        #                     WechatMessageType.Video.value,
        #                     WechatMessageType.Voice.value]
        return False

    def download(self, msg: WxMsg) -> str | None:
        """ 下载消息 """

        if msg.from_group():
            storage_path = self.storage_path + os.sep + f'{self.get_name(msg.roomid)}({msg.roomid})'
        else:
            storage_path = self.storage_path + os.sep + f'{self.get_name(msg.sender)}({msg.sender})'

        images_path = storage_path + os.sep + 'images'
        video_path = storage_path + os.sep + 'video'
        voice_path = storage_path + os.sep + 'voice'
        emoticon_path = storage_path + os.sep + 'emoticon'

        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
            [os.mkdir(d) or None for d in [images_path, video_path, voice_path, emoticon_path]]

        path = None
        if msg.from_group():
            name = f'{self.get_name(msg.sender, msg.roomid)}({msg.sender})'
        else:
            name = f'{self.get_name(msg.sender)}({msg.sender})'

        new_file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{name}'
        # 图片
        if msg.type == WechatMessageType.Image.value:
            path = self.wcf.download_image(msg.id, msg.extra, images_path)
        # 视频
        elif msg.type == WechatMessageType.Video.value:
            path = self.wcf.download_video(msg.id, msg.thumb, video_path)
        # 语音
        elif msg.type == WechatMessageType.Voice.value:
            path = self.wcf.get_audio_msg(msg.id, voice_path)
        # 表情包
        elif msg.type == WechatMessageType.Emoticon.value:
            path = self.get_emoticon_msg(msg, emoticon_path)

        if path is not None and os.path.exists(path):
            path = self._rename_keep_extension(path, new_file_name)

        return path

    def kick_out_member(self, room_id, wxid):
        return self.wcf.del_chatroom_members(room_id, wxid)

    def _rename_keep_extension(self, old_path, new_filename):
        path = Path(old_path)
        # 直接替换文件名并保留扩展名
        new_path = path.with_name(f"{new_filename}{path.suffix}")
        path.rename(new_path)
        return new_path

    def get_emoticon_url(self, msg):

        content = ET.fromstring(msg.content)
        emoji = content.find('./emoji')
        return emoji.attrib['cdnurl']

    def get_emoticon_msg(self, msg, path):

        def identify_image_format(file_b):
            if file_b.startswith(b'\xff\xd8'):
                return 'jpg'
            elif file_b.startswith(b'\x89PNG'):
                return 'png'
            elif file_b.startswith(b'GIF8'):
                return 'gif'
            elif file_b.startswith(b'BM'):
                return 'bmp'
            elif file_b.startswith(b'II*') or file_b.startswith(b'MM\x00*'):
                # TIFF可以是'II*'（Big-endian）或'MM\x00*'（Little-endian，注意MM后的\x00）
                # 但'MM\x00*'的前两个字节实际上是'MM'，所以我们需要检查这四个字节
                if file_b[:4] == b'MM\x00*':
                    return 'tiff'
                elif file_b[:4] == b'II*':
                    return 'tiff'
                # 否则，如果只有'MM'或'II'，我们可能需要进一步检查
            elif file_b.startswith(b'RIFF') and file_b[8:12] in (b'WEBP',):
                # WebP文件以RIFF开头，但我们需要检查接下来的四个字节是否为'WEBP'
                return 'webp'
            else:
                return None

        resp = requests.get(self.get_emoticon_url(msg), stream=True)
        suffix = identify_image_format(resp.content)
        filename = path + os.sep + 'image.' + suffix
        with open(filename, 'wb') as f:
            f.write(resp.content)

        return filename

    def get_name(self, wxid, roomid: str = None) -> str:
        if roomid:
            return self.get_member_name(roomid, wxid)
        return self.get_contact(wxid).get('name')

    def refresh_db_member(self, room_id):
        mem_dict = self.get_mem_members(room_id)
        with self.db_session() as db:
            for wxid, name in mem_dict.items():
                member = db.query(GroupMember).filter(GroupMember.room_id == room_id, GroupMember.wxid == wxid).first()
                if member is None:
                    db.add(GroupMember(
                        wxid=wxid,
                        room_id=room_id,
                        room_name=self.get_name(room_id),
                        name=name,
                        join_type=0,
                        is_leave=False,
                        is_admin=False,
                        created_by='refresh',
                        updated_by='refresh'))
                else:
                    member.name = name
                    member.room_name = self.get_name(room_id)
                    member.join_type = GroupMemberJoinType.Invite.value
                    member.is_leave = False
                    member.is_admin = False
                    member.updated_by = 'refresh'

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    self.plugin_loader.handle_message(msg)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}", e)

        self.wcf.enable_receiving_msg()
        Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

    def remove_group_member(self, room_id: str, wxid: str):
        return self.wcf.del_chatroom_members(room_id, wxid)

    def accept_new_friend(self, msg: WxMsg):
        try:
            xml = ET.fromstring(msg.content)
            v3 = xml.attrib["encryptusername"]
            v4 = xml.attrib["ticket"]
            scene = int(xml.attrib["scene"])
            self.wcf.accept_new_friend(v3, v4, scene)
            nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
            if nickName:
                # 添加了好友，更新好友列表
                self.refresh_contact()
                return nickName[0]
        except Exception as e:
            self.LOG.error(f"同意好友出错：{e}")

    def cleanup(self, sig, frame):
        self.plugin_loader.call_destroy_methods()
        self.wcf.cleanup()  # 退出前清理环境
        os._exit(-1)
