import datetime

from wcferry import WxMsg

from wechat_robot.models import UserAt
from wechat_robot.plugin_loader import GroupPrefixMessagePlugin


class AtAllPlugin(GroupPrefixMessagePlugin):
    def __init__(self, robot, need_at: bool = False):
        super().__init__(robot, need_at)
        self.AT_ALL_LIMIT = None

    def on_init(self) -> None:
        self.AT_ALL_LIMIT = self.robot.config['groups']['at_all_limit']

    @property
    def prefixes(self):
        return ['@所有人', '@all', '@全体']

    def on_prefix_message(self, msg: WxMsg, prefix: str, content: str) -> None:
        # 计算本周一和本周日的时间戳
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        start_of_week_date_time = datetime.datetime(start_of_week.year, start_of_week.month, start_of_week.day)
        end_of_week_date_time = datetime.datetime(end_of_week.year, end_of_week.month, end_of_week.day, 23, 59, 59)

        if not self.robot.is_group_admin(msg.roomid, msg.sender):

            current_time = datetime.datetime.now().time()
            start = datetime.time(6, 0)  # 6:00 AM
            end = datetime.time(22, 0)  # 10:00 PM

            if not (start <= current_time <= end):
                self.robot.send_text("现在太晚啦，就别打扰大家啦。\n请在 06:00 - 22:00 间使用本功能", msg.roomid, msg.sender)
                return
            with self.robot.db_session() as db:
                at_times = db.query(UserAt).filter(
                    UserAt.wxid == msg.sender,
                    UserAt.room_id == msg.roomid,
                    UserAt.created_by == msg.sender,
                    UserAt.created_at.between(start_of_week_date_time, end_of_week_date_time)
                ).count()

                canuse = self.AT_ALL_LIMIT - at_times if self.AT_ALL_LIMIT - at_times > 0 else 0
                head = f'【{self.robot.get_name(msg.sender, msg.roomid)}】'
                tail = f'\nat全体（可用/总次数）： {canuse - 1}/{self.AT_ALL_LIMIT}'

                if at_times > self.AT_ALL_LIMIT - 1:
                    self.robot.send_text(f'\n（可用/总次数）： 0/{self.AT_ALL_LIMIT}\n'
                                         f'你本周的 at全体 已用完\n'
                                         f'将在下周一刷新。\n', msg.roomid, msg.sender)
                    return

                db.add(UserAt(wxid=msg.sender,
                              room_id=msg.roomid,
                              at_content=msg.content,
                              created_by=msg.sender,
                              updated_by=msg.sender))

                self.robot.send_text(
                    f'{head}让我at大家说：\n\n{content}\n{tail}', msg.roomid, "notify@all")
        else:
            head = f'管理员：【{self.robot.get_name(msg.sender, msg.roomid)}】'
            self.robot.send_text(
                f'{head}让我at大家说：\n\n{content}', msg.roomid, "notify@all")

        return
