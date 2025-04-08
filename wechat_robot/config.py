#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import os

import yaml


class Config(object):
    def __init__(self) -> None:
        self.robot_config = None
        self.reload()

    def _load_config(self) -> dict:
        pwd = os.path.dirname(os.path.abspath(__file__))
        with open(f"{pwd}/config.yaml", "rb") as fp:
            yconfig = yaml.safe_load(fp)

        return yconfig

    def reload(self) -> None:
        yconfig = self._load_config()
        logging.config.dictConfig(yconfig["logging"])
        self.robot_config = yconfig["robot"]