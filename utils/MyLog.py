# -*- coding: utf-8 -*-
import os
from loguru import logger
from config.settings import BASE_DIR


class GetLogging:
    """
    日志配置
    """
    def __init__(self):
        # 错误日志
        logger.add(
            os.path.join(BASE_DIR, "logs/ERROR/{time:YYYY-MM-DD}.log"),
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            filter=lambda x: True if x["level"].name == "ERROR" else False,
            rotation="00:00", retention=7, level='ERROR', encoding='utf-8'
        )
        # 成功日志
        logger.add(
            os.path.join(BASE_DIR, "logs/SUCCESS/{time:YYYY-MM-DD}.log"),
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name} | {message}",
            filter=lambda x: True if x["level"].name == "SUCCESS" else False,
            rotation="00:00", retention=7, level='SUCCESS', encoding='utf-8',
        )
        # Default日志
        logger.add(
            os.path.join(BASE_DIR, "logs/Default/{time:YYYY-MM-DD}.log"),
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            rotation="00:00", retention=7, level='DEBUG', encoding='utf-8'
        )

        self.logger = logger

    def get(self):
        return self.logger


globalLog = GetLogging().get()
