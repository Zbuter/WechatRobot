from wcferry import WxMsg

from wechat_robot.enums import WechatMessageType
from wechat_robot.plugin_loader import PluginInterface


class AutoAcceptFriendPlugin(PluginInterface):

    def on_message(self, msg: WxMsg):
        if msg.type != WechatMessageType.VerifyMsg.value:  # 好友请求
            return
        nickname = self.robot.accept_new_friend(msg)
        self.robot.send_text(f"hi {nickname}。")
