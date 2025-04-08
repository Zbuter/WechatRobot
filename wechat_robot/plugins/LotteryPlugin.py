import re
from typing import Tuple, List

from wcferry import WxMsg

from wechat_robot import utils
from wechat_robot.enums import AwardStatus, RaffleStatus
from wechat_robot.models import Award, Raffle
from wechat_robot.plugin_loader import GroupPrefixMessagePlugin


class LotteryPlugin(GroupPrefixMessagePlugin):

    @property
    def prefixes(self) -> Tuple[str] or List[str]:
        return ('抽奖',
                'raffle',
                '中奖概率',
                '抽奖概率',
                'chance',
                '权重',
                'weight',
                '发起抽奖',
                '发布抽奖',
                'Lunch lottery',
                '公布',
                'publish',
                '抽奖列表',
                '抽奖历史',
                '抽奖资格删除',
                '抽奖资格恢复',
                '删除抽奖')

    def on_prefix_message(self, msg: WxMsg, prefix: str, content: str):
        if prefix in ('抽奖', 'raffle'):
            self.raffle(msg, content)
        elif prefix in ('中奖概率', '抽奖概率', 'chance'):
            self.chance(msg, content)
        elif prefix in ('权重', 'weight'):
            self.weight(msg, content)
        elif prefix in ('发起抽奖', '发布抽奖', 'Lunch lottery'):
            self.lunch(msg, content)
        elif prefix in ('公布', 'publish'):
            self.publish(msg, content)
        elif prefix in ('抽奖资格删除',):
            self.raffleRemove(msg, content)
        elif prefix in ('抽奖列表',):
            self.raffleList(msg, content)
        elif prefix in ('删除抽奖',):
            self.awardDel(msg, content)
        elif prefix in ('抽奖历史',):
            self.awardRecord(msg, content)

    def awardRecord(self,msg:WxMsg,content:str) -> None:
        with self.robot.db_session() as db:
            all_awards = db.query(Award).filter(
                Award.room_id == msg.roomid,
                Award.status == AwardStatus.Finish.value).all()
            reply_str = ''
            for award in all_awards:
                user_ids = award.winner.split(',')
                user_names = []
                for user_id in user_ids:
                    user_names.append(self.robot.get_name(user_id,msg.roomid))

                reply_str += (f'{self.robot.get_name(award.promoter, msg.roomid)}发起的：【{award.name}】\n'
                              f'{award.created_at}\n'
                              f'中奖人：{", ".join(user_names)}\n')
            self.robot.send_text(reply_str, msg.roomid, msg.sender)


    def raffleList(self, msg: WxMsg, content: str) -> None:
        with self.robot.db_session() as db:
            all_awards = db.query(Award).filter(
                Award.room_id == msg.roomid,
                Award.status == AwardStatus.Padding.value).all()
            reply_str = '当前有以下奖品正在抽奖：\n'
            for award in all_awards:
                reply_str += f'{self.robot.get_name(award.promoter,msg.roomid)}:【{award.name}】\n{award.remark}\n{award.created_at}\n\n'
            self.robot.send_text(reply_str,msg.roomid,msg.sender)


    def publish(self, msg: WxMsg, action: str):
        acts = re.split(r"\s+", action)
        if acts[0] == '':
            self.robot.send_text('请输入正确的参数\n例：公布 奖品名 中奖者\n 公布 奖品名 中奖概率', msg.roomid,
                                 msg.sender)
        with self.robot.db_session() as db:
            award = db.query(Award).filter(Award.room_id == msg.roomid,
                                           Award.name == acts[0],
                                           Award.status == AwardStatus.Padding.value).first()

            if award is None:
                self.robot.send_text(f'当前不存在【{acts[0]}】的抽奖。', msg.roomid, msg.sender)
                return

            if award.promoter != msg.sender:
                self.robot.send_text('只有抽奖发起者可以公布数据。', msg.roomid, msg.sender)
                return

            raffle_list = db.query(Raffle).filter(
                Raffle.status == RaffleStatus.Add.value,
                Raffle.award_id == award.id,
                Raffle.room_id == msg.roomid,
            ).all()

            if len(acts) > 1 and acts[1].strip() in ['中奖概率', '概率', '幸运值']:
                users = []
                for raffle_row in raffle_list:
                    name = self.robot.get_name(raffle_row.wxid, msg.roomid)
                    if name is not None:
                        users.append({'name': name, 'weight': raffle_row.weight, 'wxid': raffle_row.wxid})

                scores = utils.calculate_probabilities(users)

                sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

                message = f'当前共 {len(sorted_scores)} 人参与【{acts[0]}】抽奖\n中奖概率由高到低如下：\n'

                # 初始化序号计数器
                index = 1
                for key, value in sorted_scores:
                    message += f'{index}. {self.robot.get_name(key, msg.roomid, )}: {value:.2%}\n'
                    index += 1

                self.robot.send_text(message, msg.roomid)
                return

            if len(acts) > 1 and acts[1].strip() in ['结果', '中奖结果', '中奖者', '幸运儿', '欧皇', '获奖者',
                                                     '获奖人']:
                if len(raffle_list) < 1:
                    self.robot.send_text(f"还没有人参与抽奖【{acts[0]}】", msg.roomid, msg.sender)
                    return

                def string_to_int_safe(s):
                    try:
                        return int(s)
                    except ValueError:
                        return 1

                if len(acts) > 2:
                    length = string_to_int_safe(acts[2])
                else:
                    length = 1

                if len(raffle_list) < length:
                    self.robot.send_text(f"【{acts[0]}】中奖人数大于抽奖人数请重新输入。", msg.roomid, msg.sender)
                    return

                wxids = utils.weighted_lottery([{'wxid': i.wxid, 'weight': i.weight} for i in raffle_list], length)

                award.status = AwardStatus.Finish.value
                award.winner = ','.join(wxids)

                reply = f"本次抽奖【{acts[0]}】的获奖者是：\n"
                for wxid in wxids:
                    reply += f"{self.robot.get_name(wxid, msg.roomid)}\n"

                self.robot.send_text(reply, msg.roomid, ','.join(wxids))
                return

    def raffleRemove(self, msg: WxMsg, action: str):
        splits = re.split(r'\s+', action)

        wxids = self.get_at_list(msg)
        if wxids is None or len(wxids) == 0:
            self.robot.send_text("请 at你需要删除抽奖资格的人员", msg.roomid, msg.sender)
            return

        with self.robot.db_session() as db:
            award = db.query(Award).filter(
                Award.promoter == msg.sender,
                Award.status == AwardStatus.Padding.value,
                Award.name == splits[0],
                Award.room_id == msg.roomid).first()
            if award is None:
                self.robot.send_text(f"当前没有你发起的奖品：{splits[0]}", msg.roomid, msg.sender)
                return
            award_name = award.name
            award_id = award.id

            db.query(Raffle).filter(
                Raffle.award_id == award_id,
                Raffle.status == RaffleStatus.Add.value,
                Raffle.wxid.in_(wxids)
            ).update({Raffle.status: RaffleStatus.Delete.value})

            self.robot.send_text(
                f"已删除 {','.join([self.robot.get_name(wxid, msg.roomid) for wxid in wxids])} 的【{award_name}】 抽奖资格",
                msg.roomid, msg.sender)

    def raffleRestore(self, msg: WxMsg, action: str):
        splits = re.split(r'\s+', action)

        wxids = self.get_at_list(msg)
        if wxids is None or len(wxids) == 0:
            self.robot.send_text("请 at你需要恢复抽奖资格的人员", msg.roomid, msg.sender)
            return

        with self.robot.db_session() as db:
            award = db.query(Award).filter(
                Award.promoter == msg.sender,
                Award.status == AwardStatus.Padding.value,
                Award.name == splits[0],
                Award.room_id == msg.roomid).first()
            if award is None:
                self.robot.send_text(f"当前没有你发起的奖品：{splits[0]}", msg.roomid, msg.sender)
                return
            award_name = award.name
            award_id = award.id

            count = db.query(Raffle).filter(
                Raffle.award_id == award_id,
                Raffle.status == RaffleStatus.Delete.value,
                Raffle.wxid.in_(wxids)
            ).update({Raffle.status: RaffleStatus.Add.value})

            if count > 0:
                self.robot.send_text(
                    f"已恢复 {','.join([self.robot.get_name(wxid, msg.roomid) for wxid in wxids])} 的【{award_name}】 抽奖资格",
                    msg.roomid, msg.sender)

    def awardDel(self, msg: WxMsg, content: str):
        if content is None or content.strip() == '':
            self.robot.send_text("请输入要删除的奖品名称", msg.roomid, msg.sender)
            return

        with self.robot.db_session() as db:
            award = db.query(Award).filter(Award.promoter == msg.sender,
                                           Award.status == AwardStatus.Padding.value,
                                           Award.name == content,
                                           Award.room_id == msg.roomid).first()
            award.status = AwardStatus.Deleted.value
            award_id = award.id
            db.query(Raffle).filter(Raffle.award_id == award_id).update({Raffle.status: RaffleStatus.Delete.value})

            self.robot.send_text(f"已删除奖品【{content}】", msg.roomid, msg.sender)

    def lunch(self, msg: WxMsg, action: str):
        if action == '':
            self.robot.send_text(f"请输入正确的格式：\n例：发起抽奖 黑钻", msg.roomid, msg.sender)
            return

        award_and_remark = re.split(r'\s+', action)
        award_name = award_and_remark[0]
        remark = ' '.join(award_and_remark[1:])
        with self.robot.db_session() as db:
            award = db.query(
                Award).filter(
                Award.name == award_name,
                Award.status == AwardStatus.Padding.value,
                Award.room_id == msg.roomid).first()

            if award is not None:
                self.robot.send_text(f"当前已有一个正在抽奖的【{award.name}】奖品 \n", msg.roomid, msg.sender)
                return

            db.add(Award(
                name=award_name,
                status=AwardStatus.Padding.value,
                promoter=msg.sender,
                room_id=msg.roomid,
                remark=remark,
                created_by=msg.sender,
                updated_by=msg.sender))
        self.robot.send_text(f'{self.robot.get_name(msg.sender, msg.roomid)}发起了一项抽奖\n奖品是【{award_name}】\n\n'
                             f'以下功能仅有发起者和管理员可以操作：\n'
                             f'发送 "公布 {award_name} 概率" 查看所有人中奖概率 \n'
                             f'发送 "公布 {award_name} 结果" 查看中奖人并结束此次抽奖 \n'
                             f'发送 "权重 修改 {award_name} (+/-)100 @中奖者" 可修改参与者中奖权重\n'
                             f'发送 "删除抽奖 {award_name}  可删除发布的抽奖\n'
                             f'发送 "抽奖资格删除 {award_name} @中奖者" 可删除参与者抽奖资格\n'
                             f'发送 "抽奖资格恢复 {award_name} @中奖者" 可恢复参与者抽奖资格\n\n'
                             f'以下功能所有人均可操作：\n'
                             f'发送 "权重 查看 {award_name}"\n 或 "权重 查看 {award_name} @中奖者" 可查看参与者中奖权重\n'
                             f'发送 "抽奖 {award_name}" 进行报名', msg.roomid, 'notify@all')

    def raffle(self, msg: WxMsg, action: str):
        if action == '':
            self.robot.send_text("请输入需要参与的奖品名\n例如：抽奖 黑钻", msg.roomid, msg.sender)
            return
        with self.robot.db_session() as db:
            award = db.query(Award).filter(
                Award.room_id == msg.roomid,
                Award.name == action.strip(),
                Award.status == AwardStatus.Padding.value).first()

            if award is None:
                self.robot.send_text(f"当前没有正在抽奖的【{action}】奖品哦 \n", msg.roomid, msg.sender)
                return
            award_id = award.id
            raffle = db.query(Raffle).filter(
                Raffle.award_id == award_id, Raffle.wxid == msg.sender).first()
            if raffle is not None:
                self.robot.send_text(f"你当前已经参与了【{action}】的抽奖 请等待开奖。 \n", msg.roomid, msg.sender)
                if raffle.status == RaffleStatus.Delete.value:
                    self.robot.send_text(f"你的【{action}】的抽奖 资格已被移除。 \n", msg.roomid, msg.sender)
                    return
                return

            weight = 300
            db.add(Raffle(
                wxid=msg.sender,
                award_name=action.strip(),
                award_id=award_id,
                room_id=msg.roomid,
                weight=weight,
                status=RaffleStatus.Add.value,
                created_by=msg.sender,
                updated_by=msg.sender,
            ))

            self.robot.send_text(f'成功参与了【{action}】的抽奖 请等待开奖。\n'
                                 f'当前你的中奖权重为默认值：{weight}\n'
                                 f'如果不正确请联系【{self.robot.get_name(award.promoter, msg.roomid)}】修改你的权重。\n'
                                 f'具体规则可 @我 并发送 "抽奖规则"查看\n'
                                 f'发送 "中奖概率 {action}" 查看当前中奖概率\n'
                                 f'发送 "权重 查看 {action}" 查看当前权重\n'
                                 f'发送 "抽奖列表" 查看所有未开奖的抽奖奖品\n'
                                 f'发送 "抽奖历史" 查看往期中奖人员\n ', msg.roomid, msg.sender)

    def chance(self, msg: WxMsg, action: str):
        if action == '':
            self.robot.send_text("请输入查询您中奖概率的奖品\n例如：中奖概率 黑钻\n中奖概率 黑钻 @要查看的人",
                                 msg.roomid, msg.sender)
            return
        acts = re.split(r'\s+', action)

        wxid = msg.sender
        if len(self.get_at_list(msg)) > 0:
            wxid = self.get_at_list(msg)[0]

        with self.robot.db_session() as db:
            award = db.query(Award).filter(
                Award.name == acts[0],
                Award.status == AwardStatus.Padding.value,
                Award.room_id == msg.roomid).first()
            if award is None:
                self.robot.send_text(f"当前没有正在抽奖的【{action[1]}】奖品哦 \n", msg.roomid, msg.sender)
                return

            raffle_rows = db.query(Raffle).filter(Raffle.award_id == award.id,
                                                  Raffle.status == RaffleStatus.Add.value).all()

            users = []
            for raffle_row in raffle_rows:
                name = self.robot.get_name(raffle_row.wxid, msg.roomid)
                if name is not None:
                    users.append({'name': name, 'weight': raffle_row.weight, 'wxid': raffle_row.wxid})

            data = utils.calculate_probabilities(users)

            probabilities = data.get(wxid)
            if probabilities is None:
                probabilities = 0
            self.robot.send_text(
                f"当前【@{self.robot.get_name(wxid, msg.roomid)}】抽奖的【{acts[0]}】\n中奖概率为： {probabilities:.2%}\n",
                msg.roomid, msg.sender)

        return

    def weight(self, msg: WxMsg, action: str):
        acts = re.split(r"\s+", action)
        if len(acts[0]) == 0:
            self.robot.send_text('请输入正确的参数\n例：权重 修改 黑钻 +100\n 权重 查看 黑钻 @参与成员 ', msg.roomid,
                                 msg.sender)
        if acts[0] in ['修改', 'modify', 'm']:
            self.get_weight(msg, acts[1:])
            return
        elif acts[0] in ['查看', 'watch', 'w']:
            self.watch_weight(msg, acts[1:])

    def watch_weight(self, msg: WxMsg, acts):
        if len(acts) == 0:
            self.robot.send_text('请输入正确的参数\n例：权重 修改 黑钻 +100\n 权重 查看 黑钻 @参与成员 ', msg.roomid,
                                 msg.sender)
            return
        with self.robot.db_session() as db:
            award = db.query(
                Award).filter(
                Award.name == acts[0],
                Award.room_id == msg.roomid,
                Award.status == AwardStatus.Padding.value
            ).first()
            if award is None:
                self.robot.send_text(f'当前不存在名为【{acts[0]}】的抽奖哦。', msg.roomid, msg.sender)
                return
            at_list = self.get_at_list(msg)

            wxid = msg.sender
            if len(at_list) > 1:
                self.robot.send_text(
                    '请输入正确的参数\n例：权重 修改 黑钻 +100\n 权重 查看 黑钻 @参与成员 \n使用："权重 查看 黑钻" 查看自己的权重',
                    msg.roomid, msg.sender)
                return

            if len(at_list) == 1:
                wxid = at_list[0]

            raffle = db.query(Raffle).filter(
                Raffle.award_id == award.id,
                Raffle.status == RaffleStatus.Add.value,
                Raffle.wxid == wxid,
            ).first()

            if raffle is None:
                self.robot.send_text(
                    f'【{self.robot.get_name(wxid, msg.roomid)}】好像还没有参与抽奖哦 发送：\n抽奖 {acts[0]} 参与后即可查看',
                    msg.roomid,
                    msg.sender)
                return

            self.robot.send_text(f'{self.robot.get_name(wxid, msg.roomid)}的权重为{raffle.weight}', msg.roomid,
                                 msg.sender)

    def get_weight(self, msg, acts):
        if len(acts) == 0:
            self.robot.send_text('请输入正确的参数\n例：权重 修改 黑钻 +100\n 权重 查看 黑钻 @参与成员 ', msg.roomid,
                                 msg.sender)
            return

        number = self.number_convert(acts[1])
        with self.robot.db_session() as db:
            award = db.query(Award).filter(
                Award.name == acts[0],
                Award.room_id == msg.roomid,
                Award.status == AwardStatus.Padding.value).first()
            if award is None:
                self.robot.send_text(
                    '不存在此抽奖。\n请输入正确的参数\n例：权重 修改 黑钻 +100\n 权重 查看 黑钻 @参与成员 ',
                    msg.roomid, msg.sender)
                return

            if award.promoter != msg.sender:
                self.robot.send_text(
                    f'只有抽奖发起者可以修改权重哦 要修改请联系【{self.robot.get_name(award.promoter, msg.roomid)}】。',
                    msg.roomid, msg.sender)
                return

            ids = [x for x in self.get_at_list(msg)]
            result_msg = ''
            raffles = db.query(Raffle).filter(Raffle.wxid.in_(ids), Raffle.status == RaffleStatus.Add).all()

            if len(raffles) == 0:
                self.robot.send_text("查无此人，改不了一点。", msg.roomid, msg.sender)
                return
            for raffle in raffles:
                raffle.weight = raffle.weight + number
                r_name = self.robot.get_name(raffle.wxid, msg.roomid)
                r_weight = raffle.weight
                result_msg += f'【{r_name}】当前权重为：{r_weight}\n'

            self.robot.send_text(result_msg, msg.roomid, msg.sender)
        return

    def number_convert(self, s):
        pattern = r'^\s*[+-]?\d+\s*$'
        if re.match(pattern, s):
            # 去除字符串两端的空白字符后转换为整数
            return int(s.strip())
        else:
            return None
