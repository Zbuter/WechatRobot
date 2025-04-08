#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from argparse import ArgumentParser

from wcferry import Wcf

from wechat_robot.config import Config
from wechat_robot.robot import Robot
import logging


def main():
    config = Config()

    robot = Robot(config)
    robot.run()

if __name__ == "__main__":
    main()
