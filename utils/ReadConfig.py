# -*- coding: utf-8 -*-
from configparser import ConfigParser


class ReadConfig(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.cp = ConfigParser()
        self.cp.read(config_path)

    def get_value(self, section, key):
        value = self.cp.get(section, key)
        return value
