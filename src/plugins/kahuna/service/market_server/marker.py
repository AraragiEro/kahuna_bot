from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from peewee import fn

from ..database_server.model import MarketOrder as M_MarketOrder, MarketOrderCache as M_MarketOrderCache
from ..database_server.connect import db
from ..evesso_server.eveesi import markets_region_orders
from ..evesso_server.eveesi import markets_structures
from ..evesso_server.eveutils import find_max_page, get_multipages_result

from ...utils import KahunaException

# 查价缓存
from ..database_server.TTL_cache import ROUGE_PRICE_CACHE
from cachetools import cached

# kahuna logger
from ..log_server import logger

REGION_FORGE_ID = 10000002
JITA_TRADE_HUB_STRUCTURE_ID = 60003760
FRT_4H_STRUCTURE_ID = 1035466617946

class Market:
    market_type = "jita"
    access_character = None

    def __init__(self, market_type="jita"):
        self.market_type = market_type
        if market_type == "jita":
            self.location_id = JITA_TRADE_HUB_STRUCTURE_ID
        else:
            self.location_id = FRT_4H_STRUCTURE_ID

    def set_access_character(self, access_character):
        self.access_character = access_character

    def get_market_order(self):
        if self.market_type == "jita":
            self.get_jita_order()
        if self.market_type == "frt":
            self.get_frt_order()

    def get_frt_order(self):
        if not self.access_character:
            return
        ac_token = self.access_character.ac_token
        max_page = find_max_page(markets_structures, ac_token, FRT_4H_STRUCTURE_ID)
        # with db.atomic() as txn:
        results = get_multipages_result(markets_structures, max_page, self.access_character.ac_token, FRT_4H_STRUCTURE_ID)
        # with ThreadPoolExecutor(max_workers=100) as executor:
        #     futures = [executor.submit(markets_structures, page, ac_token, FRT_4H_STRUCTURE_ID) for page in range(1, max_page + 1)]
        #     results = []
        #     count = 1
        #     for future in tqdm(futures, desc="请求市场数据", unit="page"):
        #         result = future.result()
        #         results.append(result)
        #         count += 1

        with db.atomic():
            M_MarketOrder.delete().where(M_MarketOrder.location_id == FRT_4H_STRUCTURE_ID).execute()
            with tqdm(total=len(results), desc="写入数据库", unit="page") as pbar:
                for i, result in enumerate(results):
                    # result = [order for order in result if order["location_id"] == JITA_TRADE_HUB_STRUCTURE_ID]
                    M_MarketOrder.insert_many(result).execute()
                    pbar.update()

    def get_jita_order(self):
        max_page = find_max_page(markets_region_orders, REGION_FORGE_ID)
        # with db.atomic() as txn:

        logger.info("请求市场。")
        results = get_multipages_result(markets_region_orders, max_page, REGION_FORGE_ID)
        # with ThreadPoolExecutor(max_workers=100) as executor:
        #     futures = [executor.submit(markets_region_orders, page, REGION_FORGE_ID) for page in range(1, max_page+1)]
        #     results = []
        #     count = 1
        #     for future in tqdm(futures, desc="请求市场数据", unit="page"):
        #         result = future.result()
        #         results.append(result)
        #         count += 1

        with db.atomic():
            M_MarketOrder.delete().where(M_MarketOrder.location_id == JITA_TRADE_HUB_STRUCTURE_ID).execute()
            with tqdm(total=len(results), desc="写入数据库", unit="page") as pbar:
                for i, result in enumerate(results):
                    result = [order for order in result if order["location_id"] == JITA_TRADE_HUB_STRUCTURE_ID]
                    M_MarketOrder.insert_many(result).execute()
                    pbar.update()

    def get_market_detail(self) -> tuple[int, int, int, int]:
        if self.market_type == "jita":
            target_location = JITA_TRADE_HUB_STRUCTURE_ID
        else:
            target_location = FRT_4H_STRUCTURE_ID

        # 统计总数据数量，并按照is_buy_order进行求和统计
        total_count = (M_MarketOrder
                       .select(fn.COUNT(M_MarketOrder.id))
                       .where(M_MarketOrder.location_id == target_location)
                       .scalar())

        buy_count = (M_MarketOrder
                     .select(fn.COUNT(M_MarketOrder.id))
                     .where((M_MarketOrder.location_id == target_location) &
                            (M_MarketOrder.is_buy_order == True))
                     .scalar())

        sell_count = (M_MarketOrder
                      .select(fn.COUNT(M_MarketOrder.id))
                      .where((M_MarketOrder.location_id == target_location) &
                             (M_MarketOrder.is_buy_order == False))
                      .scalar())

        # 统计不同的类型数量
        distinct_type_count = (M_MarketOrder
                               .select(M_MarketOrder.type_id)
                               .where(M_MarketOrder.location_id == target_location)
                               .distinct()
                               .count())

        return total_count, buy_count, sell_count, distinct_type_count


    @cached(ROUGE_PRICE_CACHE)
    def get_type_order_rouge(self, type_id: int):
        if self.market_type == "jita":
            target_location = JITA_TRADE_HUB_STRUCTURE_ID
        else:
            target_location = FRT_4H_STRUCTURE_ID
        
        target_id , target_location = type_id, target_location  # replace with actual values
        
        # 获取 is_buy_order=1 的最高价格
        max_price_buy = (M_MarketOrderCache
                         .select(fn.MAX(M_MarketOrderCache.price))
                         .where((M_MarketOrderCache.type_id == target_id) &
                                (M_MarketOrderCache.location_id == target_location) &
                                (M_MarketOrderCache.is_buy_order == True))
                         .scalar())
        
        # 获取 is_buy_order=0 的最低价格
        min_price_sell = (M_MarketOrderCache
                          .select(fn.MIN(M_MarketOrderCache.price))
                          .where((M_MarketOrderCache.type_id == target_id) &
                                 (M_MarketOrderCache.location_id == target_location) &
                                 (M_MarketOrderCache.is_buy_order == False))
                          .scalar())
        if not max_price_buy or not min_price_sell:
            raise KahunaException('order data not exist in cache.')
        return float(max_price_buy), float(min_price_sell)
