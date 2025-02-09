import os
if os.environ.get('KAHUNA_BOT_TEST') != '1':
    from nonebot import require
    require("nonebot_plugin_apscheduler")
    from nonebot_plugin_apscheduler import scheduler

import asyncio
import time
import threading
from datetime import datetime
from nonebot import require


from ..database_server.model import MarketOrderCache
from ..database_server.connect import db
from .marker import Market
from ..character_server.character_manager import CharacterManager

# kahuna logger
from ..log_server import logger

class MarketManager:
    market_dict = dict()
    monitor_process = None
    refresh_signal_flag = False
    last_refresh_time = None

    @classmethod
    def init_market(cls):
        frt_market = Market("frt")
        jita_market = Market("jita")

        frt_market.access_character = CharacterManager.character_dict[2115643725]

        cls.market_dict["jita"] = frt_market
        cls.market_dict["frt"] = jita_market

    @classmethod
    def copy_to_cache(cls):
        with db.atomic():
            MarketOrderCache.delete().execute()
            db.execute_sql("INSERT INTO market_order_cache SELECT * FROM market_order")
            logger.info("copy data to cache complete")

    # 监视器，定时刷新
    @classmethod
    def refresh_market(cls):
        for market in cls.market_dict.values():
            market.get_market_order()
        cls.copy_to_cache()

        log = cls.get_markets_detal()
        logger.info(log)
        return log

    @classmethod
    def get_markets_detal(cls) -> str:
        res = {}
        for market in cls.market_dict.values():
            res[market.market_type] = market.get_market_detail()
        refresh_log = ""
        for market, date in res.items():
            refresh_log += (f"{market}:\n"
                            f"  总订单数量：{date[0]} (收单：{date[1]}, 出单：{date[2]}, 物品：{date[3]})\n")
        return refresh_log

MarketManager.init_market()
if os.environ.get('KAHUNA_BOT_TEST') != '1':
    scheduler.add_job(MarketManager.refresh_market, "interval", minutes=20)