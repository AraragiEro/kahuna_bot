from ..sde_service.utils import get_id_by_name
from ..market_server.market_manager import MarketManager

from ...utils import KahunaException

class PriceService:
    @staticmethod
    def get_price_rouge(item_str: str, market_str: str):
        # 可能的模糊匹配

        if market_str == "jita" or market_str == "frt":
            market = MarketManager.market_dict[market_str]
        else:
            raise KahunaException("market_server not define.")

        # 获取市场
        if (type_id := get_id_by_name(item_str)) is None:
            raise KahunaException("item not found.")

        max_buy, min_sell = market.get_type_order_rouge(type_id)

        # 整理信息
        mid_price = round((max_buy + min_sell) / 2, 2)

        return max_buy, mid_price, min_sell




