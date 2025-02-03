import time
import threading

from ..database_server.model import MarketOrderCache
from ..database_server.connect import db
from .marker import Market
from ..character_server.character_manager import CharacterManager

# kahuna logger
from ..log_server import logger

class MarketManager:
    market_dict = dict()
    monitor_process = None

    @classmethod
    def init_market(cls):
        frt_market = Market("frt")
        jita_market = Market("jita")

        frt_market.access_character = CharacterManager.character_dict[2115643725]

        cls.market_dict["jita"] = frt_market
        cls.market_dict["frt"] = jita_market

        # 启动监视线程
        cls.monitor_process = threading.Thread(target=cls.market_monior_process).start()

    @classmethod
    def copy_to_cache(cls):
        with db.atomic():
            MarketOrderCache.delete().execute()
            db.execute_sql("INSERT INTO market_order_cache SELECT * FROM market_order")
            logger.info("copy data to cache complete")

    @classmethod
    def market_monior_process(cls):
        time.sleep(60 * 10)
        while True:
            for market in cls.market_dict.values():
                market.get_market_order()
            cls.copy_to_cache()
            time.sleep(60 * 20)

MarketManager.init_market()