from sqlalchemy import create_engine

from wechat_robot.config import Config
from wechat_robot.models import Base

def init_database():
    config = Config()

    engine = create_engine(config.robot_config['database_url'])
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    init_database()

