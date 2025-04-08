import re
import threading
import time

from wcferry import WxMsg

from wechat_robot.enums import WechatMessageType, GroupMemberJoinType
from wechat_robot.models import GroupMember, NameHistory
from wechat_robot.plugin_loader import GroupPlugin


class MembershipAlertPlugin(GroupPlugin):
    def on_init(self) -> None:

        self.robot.onEverySeconds(10, self._group_job)

    def on_group_message(self, msg: WxMsg, room_id: str):
        if msg.type != WechatMessageType.Sys.value:  # 系统信息
            return

        if re.search(r'拍了拍我', msg.content):
            self.robot.send_pat(msg.roomid, msg.sender)
            return

        (joiner, join_type) = self._extract_new_member_name(msg.content)

        if joiner is not None:
            wxid = self.get_new_join_wxid(msg.roomid, joiner)
            with self.robot.db_session() as db:
                db.add(GroupMember(
                    wxid=wxid,
                    room_id=msg.roomid,
                    name=joiner,
                    is_leave=False,
                    is_admin=False,
                    created_by=wxid,
                    updated_by=wxid,
                    join_type=GroupMemberJoinType.Invite.value))
            self.new_join_message(wxid, joiner, msg.roomid)
        return

    def get_new_join_wxid(self, roomid: str, name: str):
        mem_members = self.robot.get_mem_members(roomid)
        for w, n in mem_members.items():
            if name == n:
                return w
        time.sleep(1)
        self.robot.refresh_mem_member(roomid)
        return self.get_new_join_wxid(roomid, name)

    def onGroupMessage(self, msg: WxMsg, roomid):
        if not (msg.is_at(self.robot.wxid) and re.sub(r'\s*@.*?\s+', '', msg.content) == '抽奖规则'):
            return
        self.robot.wcf.send_image(r'https://s21.ax1x.com/2025/03/08/pEtcF3D.png', roomid)
        # self.robot.wcf.forward_msg(msg.id, msg.roomid)
        return

    def new_join_message(self, wxid, joiner, room_id):
        data = f'''[庆祝] 欢迎新成员【{joiner}】加入

    🌟 公会名：【{self.robot.get_contact(room_id).get('name')}】 

    📝 请尽快将 群昵称 修改为游戏id 
       2 小时后未修改会被移出群聊。
      (冒险团名 或冒险团内任意角色名)


    💡Tips:
       1. 游戏离线太久会被踢出工会哦。
       2. 群里不要发黄图 也别聊政治 可能会被移出群聊。
       3. 进群 2 小时没有修改群名片会被移除群聊。
       4. 每周有抽奖活动 具体细节可以 @我 并发送 "抽奖规则"。
               '''
        self.robot.send_text(data, room_id)

        # 设置一个定时器，120分钟后执行my_task

        timer2 = threading.Timer(30 * 60, self.check_need_rename, args=[wxid, joiner, room_id])
        timer3 = threading.Timer(60 * 60, self.check_need_rename, args=[wxid, joiner, room_id])
        timer4 = threading.Timer(90 * 60, self.check_need_rename, args=[wxid, joiner, room_id])
        timer1 = threading.Timer(120 * 60, self.check_rename, args=[wxid, joiner, room_id])

        timer1.start()
        timer2.start()
        timer3.start()
        timer4.start()
        return

    def check_rename(self, wxid, joiner, room_id):
        if joiner == self.robot.get_name(wxid, room_id):
            self.robot.send_text(f"【{joiner}】 因2小时内未修改群名片 已被移出群聊", room_id, wxid)
            self.robot.remove_group_member(room_id, wxid)
        return

    def check_need_rename(self, wxid, joiner, room_id):
        if joiner == self.robot.get_name(wxid, room_id):
            self.robot.send_text(f"【{joiner}】 请尽快修改群名片，超过2小时将会被移出群聊", room_id, wxid)
        return

    def group_member_leave(self, wxid, nick_name, room_id):
        data = f'''【{nick_name}】永远的离开了我们'''
        self.robot.send_text(data, room_id)
        return

    def group_member_name_change(self, wxid, roomid, old_name, new_name):
        data = f'''【{old_name}】刚刚将名字改为了：【{new_name}】'''
        self.robot.send_text(data, roomid)

    def _extract_new_member_name(self, content):
        """
        从消息内容中抽取新加入群聊的成员名字。

        :param content: 消息内容字符串
        :return: 成员名字或None（如果没有匹配）
        """
        # 合并后的正则表达式，更精确地匹配两种情况
        pattern = r'"([^"]+)"(?:加入了群聊|通过.*?加入群聊)|([^"]+)通过.*?加入群聊'

        match = re.search(pattern, content)

        if match:
            # 提取第一个非空匹配组作为成员名字
            for group in match.groups():
                if group:  # 如果找到了非空的匹配
                    return group.strip(), content  # 移除可能存在的前后空白字符

        return None, ''  # 如果没有找到匹配项

    def _check_user_leave(self, room_id):
        with self.robot.db_session() as db:

            db_member_list = db.query(GroupMember).filter(GroupMember.room_id == room_id,
                                                          GroupMember.is_leave == False).all()
            in_group_wxids = self.robot.get_mem_members(room_id).keys()
            leave_users = {}

            if in_group_wxids is None or len(in_group_wxids) == 0:
                return

            for db_member in db_member_list:
                if db_member.wxid not in in_group_wxids:
                    leave_users[db_member.wxid] = db_member.name
                    user = db.query(GroupMember).filter(GroupMember.id == db_member.id).first()
                    user.is_leave = True

            if len(leave_users) > 0:
                for u, n in leave_users.items():
                    self.group_member_leave(u, n, room_id)




    def _check_user_name(self, room_id):
        with self.robot.db_session() as db:
            db_member_list = db.query(GroupMember).filter(GroupMember.room_id == room_id,
                                                          GroupMember.is_leave == False).all()
            mem_members_dict = self.robot.get_mem_members(room_id)

            if len(db_member_list) == 0:
                db_member_list = self.init_db_member(room_id, mem_members_dict)

            for member in db_member_list:
                wxid = member.wxid
                new_name = mem_members_dict.get(wxid)
                old_name = member.name
                if new_name is None or new_name == '':
                    continue

                if old_name is not None and old_name != new_name:
                    member.name = new_name
                    db.add(NameHistory(
                        wxid=wxid,
                        room_id=room_id,
                        old_name=old_name,
                        new_name=new_name,
                        created_by=wxid,
                        updated_by=wxid
                    ))
                    self.group_member_name_change(
                        wxid,
                        room_id,
                        old_name=old_name,
                        new_name=new_name)

        return

    def init_db_member(self, roomid, mem_members_dict=None):
        """
        初始化数据库群成员
        """

        list_mem = []
        with self.robot.db_session() as db:
            for wxid, name in mem_members_dict.items():
                db.add(GroupMember(
                    wxid=wxid,
                    room_id=roomid,
                    room_name=self.robot.get_name(roomid),
                    name=name,
                    join_type=0,
                    is_leave=False,
                    is_admin=False,
                    created_by='init',
                    updated_by='init'))
        return list_mem

    def _group_job(self):
        for room_id in self.robot.config['groups']['enable']:
            self.robot.refresh_mem_member(room_id)
            self._check_user_leave(room_id)
            self._check_user_name(room_id)
        return
