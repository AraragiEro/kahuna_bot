import asyncio
from pickle import BINPUT

from .industry_analyse import IndustryAnalyser
from ..sde_service.utils import SdeUtils
from ..user_server.user_manager import UserManager
from ..user_server.user import User
from ...utils import KahunaException
from ..market_server.marker import MarketHistory
from ..market_server.market_manager import MarketManager

class IndustryAdvice:
    @classmethod
    def advice_report(cls, user: User, plan_name: str, product_list: list):
        jita_mk = MarketManager.get_market_by_type('jita')
        vale_mk = MarketManager.get_market_by_type('frt')

        input_list = product_list
        t2_ship_id_list = [SdeUtils.get_id_by_name(name) for name in input_list]
        t2_plan = [[ship, 1] for ship in input_list]

        t2_cost_data = IndustryAnalyser.get_cost_data(user, plan_name, t2_plan)
        t2_cost_data = [[name] + value for name, value in t2_cost_data.items()]
        t2ship_data = []
        for data in t2_cost_data:
            tid = SdeUtils.get_id_by_name(data[0])
            vale_mk_his_data, forge_mk_his_data = MarketHistory.get_type_history_detale(tid)
            frt_buy, frt_sell = vale_mk.get_type_order_rouge(tid)
            jita_buy, jita_sell = jita_mk.get_type_order_rouge(tid)

            market_data = [
                tid,        # id
                data[0],    # name
                SdeUtils.get_cn_name_by_id(tid), # cn_name
                frt_sell * 0.956 - data[3] * 1.01,  # 利润
                (frt_sell * 0.956 - data[3] * 1.01) / data[3],  # 利润率
                vale_mk_his_data['monthflow'] * ((frt_sell * 0.956 - data[3] * 1.01) / data[3]), # 月利润空间
                data[3],    # cost
                frt_sell,   # 4h出单
                jita_buy,   # 吉他收单
                jita_sell,  # 吉他出单
                vale_mk_his_data['monthflow'],  # 月流水
                vale_mk_his_data['month_volume'], # 月销量
                SdeUtils.get_metaname_by_typeid(tid)    # 元组信息
            ]


            t2ship_data.append(market_data)

        t2ship_data.sort(key=lambda x: x[5], reverse=True)
        return t2ship_data