import random
from contextlib import contextmanager
from datetime import datetime, date
from typing import Type, Any, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import and_

from wechat_robot.models import Base, Award


class DatabaseManager:
    def __init__(self, database_url: str):
        """
        初始化数据库管理器。

        :param database_url: 数据库连接URL，例如 'mysql+pymysql://username:password@localhost:3306/dbname'
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    @contextmanager
    def session_scope(self) -> scoped_session:
        """
        提供一个事务性作用域，围绕一系列操作。

        :yield: 当前会话对象
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()



def time_in_range(time_str1, time_str2):
    # 定义时间格式，这里假设时间为 "HH:MM:SS" 格式
    time_format = "%H:%M"

    # 将字符串时间转换为 datetime 对象
    time1 = datetime.strptime(time_str1, time_format).time()
    time2 = datetime.strptime(time_str2, time_format).time()

    # 获取当前时间
    current_time = datetime.now().time()

    # 判断当前时间是否在范围内
    # 因为 time1 一定小于 time2，所以不需要考虑时间翻转的情况
    if time1 <= current_time <= time2:
        return True
    else:
        return False


def time_str(fmt="%H:%M:%S"):
    return datetime.now().strftime(fmt)


def parse_time_to_datetime(time_str: str) -> datetime:
    time_str = time_str.replace("：", ":")
    # 定义所有可能的时间格式
    time_formats = [
        ("%H:%M:%S", "%Y-%m-%d %H:%M:%S"),  # 24小时制，包含秒
        ("%H:%M", "%Y-%m-%d %H:%M"),  # 24小时制，不包含秒
        ("%I:%M:%S %p", "%Y-%m-%d %I:%M:%S %p"),  # 12小时制，包含秒和AM/PM
        ("%I:%M %p", "%Y-%m-%d %I:%M %p")  # 12小时制，不包含秒和包含AM/PM
    ]

    # 尝试解析时间字符串
    for time_only_fmt, datetime_fmt in time_formats:
        try:
            # 尝试解析为纯时间
            time_obj = datetime.strptime(time_str, time_only_fmt)
            # 如果解析成功，说明是纯时间字符串，需要拼接日期
            today = date.today()
            # 拼接日期和时间字符串
            datetime_str = f"{today.strftime('%Y-%m-%d')} {time_str}"
            # 使用对应的日期时间格式解析拼接后的字符串
            return datetime.strptime(datetime_str, datetime_fmt)
        except ValueError:
            # 解析失败，继续尝试下一个格式
            continue

    # 如果所有格式都尝试失败，则尝试直接解析为完整的日期时间字符串
    # 注意：这里应该根据实际的输入格式来调整解析器。如果输入格式不确定，
    # 你可能需要使用第三方库如 `dateutil.parser` 来进行更灵活的解析。
    try:
        # 这里假设了一种可能的完整日期时间格式，但实际应用中应该根据输入调整
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")  # 示例格式，可能不包含秒
    except ValueError:
        # 如果仍然失败，则抛出异常
        raise ValueError(f"Cannot parse input string as time or datetime: {time_str}")


def weighted_lottery(participants, num_winners):
    # 计算总权重
    total_weight = sum(max(participant['weight'], 0) for participant in participants)

    # 如果没有参与者或者没有权重，直接返回空列表
    if total_weight == 0 or num_winners <= 0:
        return []

    # 初始化一个集合来存储中奖者，避免重复
    winners = set()

    # 当集合中的中奖者数量小于指定数量时继续抽取
    while len(winners) < num_winners:
        # 生成一个介于0和总权重之间的随机数
        random_index = random.randint(0, total_weight - 1)

        # 累加权重并查找中奖者
        cumulative_weight = 0
        for participant in participants:
            cumulative_weight += max(participant['weight'], 0)
            if random_index < cumulative_weight and participant['wxid'] not in winners:
                winners.add(participant['wxid'])
                break  # 找到一个中奖者后，跳出循环继续下一次抽取

    # 将集合转换为列表返回
    return list(winners)


def calculate_probabilities(participants):
    total_weight = sum(max(participant['weight'], 0) for participant in participants)
    probabilities = {}
    if total_weight == 0:
        return probabilities

    for participant in participants:
        probabilities[participant['wxid']] = max(participant['weight'], 0) / total_weight
    return probabilities
