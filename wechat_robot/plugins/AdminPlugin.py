import re
from typing import List

from wcferry import WxMsg

from wechat_robot.models import GroupMember
from wechat_robot.plugin_loader import PrefixMessagePlugin


class AdminPlugin(PrefixMessagePlugin):

    @property
    def prefixes(self):
        return ['踢人', 'kickout', '踢出', '删除', '添加管理', '删除管理', '管理列表']

    def on_prefix_message(self, msg: WxMsg, prefix: str, content: str) -> None:
        if not self._sender_is_admin(msg.sender, msg.roomid):
            self.robot.send_text(f"只有管理员才可以使用【{prefix}】功能。", msg.roomid, msg.sender)
            return

        if prefix in ('踢人', 'kickout', '踢出', '删除',):
            if not self._sender_is_admin(msg.sender, msg.roomid):
                self.robot.send_text("只有管理员才可以踢人。", msg.roomid, msg.sender)
                return

            if msg.from_group():
                self.robot.refresh_db_member(msg.roomid)
                self.from_group(msg)
            else:
                rooms = self.robot.config['groups']['enable']
                for room in rooms:
                    self.robot.refresh_db_member(room)
                self.from_user(msg, content)
        elif msg.from_group() and prefix in ('添加管理',):
            self.add_admin(self._get_at_list(msg), msg.roomid, msg.sender)

        elif msg.from_group() and prefix in ('删除管理',):
            self.del_admin(self._get_at_list(msg), msg.roomid, msg.sender)
        elif msg.from_group() and prefix in ('管理列表',):
            self.admin_list(msg.roomid, msg.sender)

    def add_admin(self, add_wxids: List[str], room_id: str, sender: str) -> None:
        if sender not in self.robot.config['admins']:
            self.robot.send_text(f'添加删除管理需具备超级管理员权限', sender)
            return
        admin_names = []
        with self.robot.db_session() as db:
            group_members = db.query(GroupMember).filter(
                GroupMember.wxid.in_(add_wxids),
                GroupMember.room_id == room_id).all()

            for group_member in group_members:
                group_member.is_admin = True
                admin_names.append(group_member.name)

            self.robot.send_text(f'已添加管理：{", ".join(admin_names)}', sender)

    def del_admin(self, remove_wxids: List[str], room_id: str, sender: str) -> None:
        if sender not in self.robot.config['admins']:
            self.robot.send_text(f'添加删除管理需具备超级管理员权限', sender)
            return
        admin_names = []
        with self.robot.db_session() as db:
            group_members = db.query(GroupMember).filter(
                GroupMember.wxid.in_(remove_wxids),
                GroupMember.room_id == room_id).all()

            for group_member in group_members:
                group_member.is_admin = False
                admin_names.append(group_member.name)

            self.robot.send_text(f'已移除管理：{", ".join(admin_names)}', sender)

    def admin_list(self, room_id: str, sender: str) -> None:

        with self.robot.db_session() as db:
            group_admins = db.query(GroupMember).filter(
                GroupMember.is_admin == True,
                GroupMember.room_id == room_id).all()

            admin_names = [admin.name for admin in group_admins]
        self.robot.send_text(f'当前群组的管理有：\n {" ".join(admin_names)}', sender)

    def from_group(self, msg: WxMsg):
        wxids = self._get_at_list(msg)

        if len(wxids) == 0:
            self.robot.send_text("踢人的话需要 at上需要踢的人哦", msg.roomid, msg.sender)
        wxid = wxids[0]
        w = self._del_member(msg.roomid, wxids[0])
        if w:
            self.robot.send_text(f"{self.robot.get_name(wxid, msg.roomid)}已踢出", msg.roomid, msg.sender)
        else:
            self.robot.send_text(f"{self.robot.get_name(wxid, msg.roomid)}踢出失败", msg.roomid, msg.sender)

    def from_user(self, msg: WxMsg, content):
        with self.robot.db_session() as db:
            sender_with_group = db.query(GroupMember).filter(GroupMember.wxid == msg.sender).all()

            if len(sender_with_group) == 0:
                self.robot.send_text("抱歉，没有找到你管理的群。", msg.sender)
                return

            if len(sender_with_group) > 1:
                split = re.split(r'##', content)
                if len(split) < 2:
                    self.robot.send_text(
                        "请输入正确的命令: 删除 成员名##[群聊名]\n 如果仅有一个管理群可不输入##与群聊名",
                        msg.sender)
                    return

                filters = [GroupMember.name == split[0], GroupMember.room_name == split[1]]
            else:
                filters = [GroupMember.name == content]
            member = db.query(GroupMember).filter(*filters).first()
            del_room_id = member.room_id
            del_member_wxid = member.wxid
            w = self._del_member(del_room_id, del_member_wxid)

            if w:
                self.robot.send_text(
                    f"已将【{self.robot.get_name(del_member_wxid, del_room_id)}】从【{self.robot.get_name(del_room_id)}】踢出",
                    msg.sender)
            else:
                self.robot.send_text(
                    f"将【{self.robot.get_name(del_member_wxid, del_room_id)}】从【{self.robot.get_name(del_room_id)}】 踢出失败",
                    msg.sender)

    def _sender_is_admin(self, sender: str, room_id=None) -> bool:
        if sender in self.robot.config['super_admins']:
            return True
        with self.robot.db_session() as db:
            sender = db.query(GroupMember).filter(GroupMember.wxid == sender, GroupMember.room_id == room_id).first()
            if sender is None:
                return False
            return sender.is_admin

    def _del_member(self, room_id: str, wxid: str):

        ret = self.robot.kick_out_member(room_id, wxid)
        if ret != 1:
            self.robot.LOG(f'删除成员失败，room_id={room_id} sender={wxid} ret={ret}')
            return None

        with self.robot.db_session() as db:
            member = db.query(GroupMember).filter(GroupMember.wxid == wxid, GroupMember.room_id == room_id).first()
            member.is_leave = True

        return wxid

    def _get_at_list(self, msg: WxMsg):
        data = re.search(r'<atuserlist>\s*(?:<!\[CDATA\[)?(.*?)(?:]]>)?\s*</atuserlist>', msg.xml)
        if data is not None:
            return [wxid for wxid in data[1].split(',') if wxid]
        return []
