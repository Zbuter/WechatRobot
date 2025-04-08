from wcferry import WxMsg

from wechat_robot.enums import WechatMessageType, get_enum_by_value
from wechat_robot.models import ChatHistory
from wechat_robot.plugin_loader import PluginInterface


class MessageStoragePlugin(PluginInterface):
    def on_message(self, msg: WxMsg) -> None:
        room_id = None
        content = msg.content
        if msg.from_group() and msg.roomid not in self.robot.config['groups']['enable']:
            return

        if msg.from_group():
            name = self.robot.get_member_name(msg.roomid, msg.sender)
            room_id = msg.roomid
        else:
            contact = self.robot.get_contact(msg.sender)
            name = contact.get('name')

        if self.robot.can_download(msg):
            content = self.robot.download(msg)

        message_type = get_enum_by_value(WechatMessageType, msg.type)
        if message_type is None:
            msg_type = msg.type
        else:
            msg_type = message_type.name

        if msg.type == WechatMessageType.Emoticon.value:
            pass
        elif msg.type == WechatMessageType.Image.value:
            pass


        else:
            self.robot.LOG.info(
                f'[{msg_type}]===【{self.robot.get_contact(room_id).get("name") if room_id else "私聊消息"}({room_id}): '
                f'{self.robot.get_member_name(room_id, msg.sender) if room_id else self.robot.get_name(msg.sender)}({msg.sender})】: {content}')

        with self.robot.db_session() as db:
            db.add(
                ChatHistory(name=name if name is not None else "System",
                            wxid=msg.sender if msg.sender is not None else "System",
                            room_id=room_id,
                            room_name=self.robot.get_contact(room_id).get("name") if room_id else None,
                            content=content,
                            msg_id=msg.id,
                            type=msg.type,
                            xml=msg.xml,
                            created_by=msg.sender if msg.sender is not None else "System",
                            updated_by=msg.sender if msg.sender is not None else "System",))
