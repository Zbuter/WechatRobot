import importlib.util
import os
import re
import xml.etree.ElementTree as ET
from typing import List, Dict

from wcferry import WxMsg

from wechat_robot.enums import WechatMessageType
from wechat_robot.exceptions import RobotProcessMessageException, RobotException


class PluginInterface:
    def __init__(self, robot):
        self.robot = robot  # 机器人实例，插件可以通过这个实例与机器人进行交互
        self.SUPER_ADMINS = self.robot.config['super_admins']

    def on_init(self) -> None:
        """初始化调用"""
        pass

    def on_destroy(self) -> None:
        """销毁时调用"""
        pass

    def on_message(self, msg: WxMsg) -> None:
        """处理接收到的消息"""
        pass

    def before_msg_send(self, msg: str | Dict, receiver: str, **kw) -> bool:
        """ 发送消息前 """
        pass

    def after_msg_send(self, msg: str | Dict, receiver: str, **kw) -> None:
        """ 发送消息后 """
        pass

    def on_error(self, e) -> None:
        raise RobotException(e)


class GroupPlugin(PluginInterface):
    def __init__(self, robot, need_at: bool = False):
        super().__init__(robot)
        self.need_at = need_at
        self.GROUPS = self.robot.config['groups']['enable']

    def on_message(self, msg: WxMsg) -> None:
        if not msg.from_group():
            return
        # 需要 at 但是没at的消息跳过
        if self.need_at and not msg.is_at(self.robot.self_wxid):
            return
        if msg.roomid not in self.GROUPS:
            return
        self.on_group_message(msg, msg.roomid)

    def on_group_message(self, msg: WxMsg, room_id: str) -> None:
        """
        收到群消息时调用。 重写 on_message 后需要手动调用
        """
        pass

    def get_at_list(self, msg: WxMsg):
        data = re.search(r'<atuserlist>\s*(?:<!\[CDATA\[)?(.*?)(?:]]>)?\s*</atuserlist>', msg.xml)
        if data is not None:
            return [wxid for wxid in data[1].split(',') if wxid]
        return []


class PrefixMessagePlugin(PluginInterface):

    @property
    def prefixes(self):
        return []

    def __init__(self, robot):
        super().__init__(robot)

    def get_text_msg(self, msg: WxMsg) -> str | None:
        # 引用 引用的消息 57 引用消息为49
        if msg.type == WechatMessageType.Text.value:
            return msg.content

        if msg.type == WechatMessageType.App.value:
            # 解析 XML 数据
            try:
                root = ET.fromstring(msg.content)
                title = root.find('.//title').text
                refermsg = root.find('.//refermsg')
                msg.xml = msg.content

                if refermsg:
                    msg.type = WechatMessageType.ReferMsg.value
                    msg.content = title
                elif root.find('.//appattach'):
                    des = root.find('.//des').text
                    appname = root.find('.//appname').text
                    msg.content = f'[{appname}]--{title}({des})'
            except ET.ParseError as e:
                # 已经被处理过会来到这里。
                return msg.content

        return None

    def match_prefix(self, msg: WxMsg) -> (str, str):
        """
        匹配前缀
        """
        text = self.get_text_msg(msg)
        if text is None:
            return None, None
        return self.get_prefix_content(text, self.prefixes)

    @classmethod
    def get_prefix_content(cls, string: str, prefixes: str | List[str]) -> (str, str):
        if type(prefixes) is str:
            prefixes = [prefixes]

        for prefix in prefixes:
            full_pattern = fr"^({prefix})\s+|^({prefix})$"
            match = re.match(full_pattern, string)
            if match is not None:
                return match.group(0).strip(), string[len(prefix):].strip()
        return None, None

    def on_message(self, msg: WxMsg) -> None:
        prefix, content = self.match_prefix(msg)
        if not prefix:
            return
        self.on_prefix_message(msg, prefix, content)

    def on_prefix_message(self, msg: WxMsg, prefix: str, content: str) -> None:
        """
        匹配到 match_prefix 返回为 True 的消息 调用
        """
        pass


class GroupPrefixMessagePlugin(GroupPlugin, PrefixMessagePlugin):

    def on_group_message(self, msg: WxMsg, room_id: str) -> None:
        prefix, content = self.match_prefix(msg)
        if not prefix:
            return
        self.on_prefix_message(msg, prefix, content)


class PluginLoader:
    def __init__(self, robot):
        self.robot = robot
        self.plugins = []

    def load_plugins(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]  # 去掉.py后缀
                module_spec = importlib.util.find_spec(f"wechat_robot.plugins.{plugin_name}")
                if module_spec:
                    module = importlib.util.module_from_spec(module_spec)
                    module_spec.loader.exec_module(module)

                    # 查找并实例化插件类
                    for attr_name, attr_value in vars(module).items():
                        if (isinstance(attr_value, type) and issubclass(attr_value, PluginInterface)
                                and attr_value is not PluginInterface):
                            plugin = attr_value(self.robot)
                            self.plugins.append(plugin)
                            print(f"Loaded plugin: {attr_name}")

    def call_init_methods(self):
        for plugin in self.plugins:
            plugin.on_init()

    def call_destroy_methods(self):
        for plugin in self.plugins:
            plugin.on_destroy()

    def handle_message(self, msg):
        for plugin in self.plugins:
            plugin.on_message(msg)

    def handle_before_send_msg(self, msg, rec, **kw):
        for plugin in self.plugins:
            acc = plugin.before_msg_send(msg, rec, **kw)
            if not acc:
                continue
        return None

    def handle_after_send_msg(self, msg, rec, **kw):
        for plugin in self.plugins:
            reply = plugin.after_msg_send(msg, rec, **kw)
            if reply:
                return reply
        return None
