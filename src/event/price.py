# import logger
from astrbot.api import logger
import imgkit
import os

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Image
# kahuna model
from .utils import kahuna_debug_info
from ..service.market_server import PriceService

# kahuna Permission
# from ..permission_checker import PermissionChecker

# import Exception
from ..utils import KahunaException

# import logger
from ..service.log_server import logger

# global value
ROUGE_PRICE_HELP = ("ojita/ofrt:\n" \
                    "   [物品]:       获得估价。\n"
                    "   [物品] * [数量]: 获得估价。\n")

class TypesPriceEvent():
    @staticmethod
    def ojita_func(event: AstrMessageEvent, require_str: str):
        return TypesPriceEvent.oprice(event, require_str, "jita")

    @staticmethod
    def ofrt_func(event: AstrMessageEvent, require_str: str):
        user_qq = kahuna_debug_info(event)
        return TypesPriceEvent.oprice(event, require_str, "frt")

    @staticmethod
    def oprice(event: AstrMessageEvent, require_str: str, market: str):
        message_str = event.get_message_str()
        if message_str.split(" ")[-1].isdigit():
            quantity = int(message_str.split(" ")[-1])
            item_name = " ".join(message_str.split(" ")[1:-1])
        else:
            item_name = require_str
            quantity = 1

        max_buy, mid_price, min_sell, fuzz_list = PriceService.get_price_rouge(item_name, market)
        if fuzz_list:
            fuzz_rely = (f"物品 {item_name} 不存在于数据库\n"
                         f"你是否在寻找：\n")
            fuzz_rely += '\n'.join(fuzz_list)
            return event.plain_result(fuzz_rely)

        print_str = (f"{item_name} price in {market}:\n"
                     f"    min_sell: {min_sell:,}\n"
                     f"    mid_price: {mid_price:,}\n"
                     f"    max_buy: {max_buy:,}\n")
        if quantity > 1:
            print_str += ("\n"
                          f"{quantity} x {item_name}:\n"
                          f"    min_sell: {(min_sell * quantity):,}\n"
                          f"    mid_price: {(mid_price * quantity):,}\n"
                          f"    max_buy: {(max_buy * quantity):,}\n")

        return event.plain_result(print_str)

    @staticmethod
    def test_func(event: AstrMessageEvent, require_str: str):
        user_qq = kahuna_debug_info(event)
        market = 'jita'

        message_str = event.get_message_str()
        if message_str.split(" ")[-1].isdigit():
            quantity = int(message_str.split(" ")[-1])
            item_name = " ".join(message_str.split(" ")[1:-1])
        else:
            item_name = require_str
            quantity = 1

        max_buy, mid_price, min_sell, fuzz_list = PriceService.get_price_rouge(item_name, market)
        # if fuzz_list:
        #     fuzz_rely = (f"物品 {item_name} 不存在于数据库\n"
        #                  f"你是否在寻找：\n")
        #     fuzz_rely += '\n'.join(fuzz_list)
        #     return event.plain_result(fuzz_rely)
        #
        # print_str = (f"{item_name} price in {market}:\n"
        #              f"    min_sell: {min_sell:,}\n"
        #              f"    mid_price: {mid_price:,}\n"
        #              f"    max_buy: {max_buy:,}\n")
        # if quantity > 1:
        #     print_str += ("\n"
        #                   f"{quantity} x {item_name}:\n"
        #                   f"    min_sell: {(min_sell * quantity):,}\n"
        #                   f"    mid_price: {(mid_price * quantity):,}\n"
        #                   f"    max_buy: {(max_buy * quantity):,}\n")
        res_path = PriceResRender.render_res_pic([max_buy, mid_price, min_sell, fuzz_list])
        chain = [
            Image.fromFileSystem(res_path)
        ]
        return event.chain_result(chain)

# TODO 临时目录的创建
tmp_path = os.path.join(os.path.dirname(__file__), "../../tmp")

class PriceResRender():
    @classmethod
    def render_res_pic(cls, price_data: list):
        max_buy, mid_price, min_sell, fuzz_list = price_data

        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>WeasyPrint 示例</title>
    <style>
        @page {
            size: A4;  /* 可以使用 A4, letter 等预定义尺寸 */
            margin: 2cm;  /* 页面边距 */
        }
        /* 或者使用具体尺寸 */
        /*
        @page {
            size: 210mm 297mm;  /* 宽度 高度 */
        }
        */
        body { 
            font-family: Arial, sans-serif;
            max-width: 800px;  /* 控制内容最大宽度 */
            margin: 0 auto;    /* 内容居中 */
        }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>WeasyPrint 示例</h1>
    <p>这是一个简单的HTML转换为PDF的示例。</p>
</body>
</html>
"""

        # output_path = os.path.join(tmp_path, "price_res.jpg")
        output_path = os.path.join('F:\WorkSpace\GIT\kahuna_bot\AstrBot\data\plugins\kahuna_bot\\tmp', "price_res.jpg")
        if imgkit.from_string(html_content, os.path.join(tmp_path, output_path)):
            return output_path
        return None



