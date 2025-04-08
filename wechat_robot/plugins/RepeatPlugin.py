import re
import threading
import time
from collections import defaultdict
from typing import Dict, Tuple, List

from wcferry import WxMsg

from wechat_robot.plugin_loader import GroupPlugin


class RepeatPlugin(GroupPlugin):
    interval = 30

    def __init__(self, robot, need_at: bool = False):
        super().__init__(robot, need_at)
        self.job = None
        self.message_counts = None

    def on_init(self):
        # 字典来存储消息内容、计数和时间戳，使用 defaultdict 初始化计数为 0
        self.message_counts: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))

    def enable_plugin(self):
        self.job = self.robot.onEverySeconds(self.interval, self._cleanup)

    def on_destroy(self) -> None:
        """销毁时调用"""
        pass
    def _cleanup(self):
        """定期清理过期条目的线程函数"""
        current_time = time.time()
        # 创建一个要删除的键列表，避免在遍历字典时修改它
        keys_to_remove = [
            key for key, (count, timestamp) in self.message_counts.items()
            if current_time - timestamp > 30
        ]
        for key in keys_to_remove:
            del self.message_counts[key]

    def on_group_message(self, msg: WxMsg,room_id:str):
        content = re.sub(r'fromusername = "(.*?)"', '', msg.content)
        content = re.sub(r'<gameext type="0" content="0" ></gameext> <extcommoninfo></extcommoninfo>', ' ', content)
        current_time = time.time()

        # 检查字典并更新计数和时间戳
        count, timestamp = self.message_counts[content]
        if current_time - timestamp <= self.interval:
            self.message_counts[content] = (count + 1, timestamp)
            if count == 2:
                self.robot.wcf.forward_msg(msg.id, msg.roomid)
        else:
            self.message_counts[content] = (1, current_time)
