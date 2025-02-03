# import logger
from astrbot.api import logger

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register

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
#
# # define event
# # 获取jita价格
# kahuna_cmd_ofrt = on_command("ofrt",
#                              permission=PermissionChecker.default_permission,
#                              priority=10, block=True)
# # 获取联盟市场价格
# kahuna_cmd_ojita = on_command("ojita",
#                               permission=PermissionChecker.default_permission,
#                               priority=10, block=True)
#
# async def kahuna_cmd_price(matcher: Matcher, event: Event, product_name: str, quantity: int, market_location: str):
#     logger.debug("go in cmd price")
#
#     try:
#         max_buy, mid_price, min_sell = PriceService.get_price_rouge(product_name, market_location)
#         print_str = (f"{product_name} price in {market_location}:\n"
#                      f"    min_sell: {min_sell:,}\n"
#                      f"    mid_price: {mid_price:,}\n"
#                      f"    max_buy: {max_buy:,}\n")
#         if quantity > 1:
#             print_str += ("\n"
#                           f"{quantity} x {product_name}:\n"
#                           f"    min_sell: {(min_sell*quantity):,}\n"
#                           f"    mid_price: {(mid_price*quantity):,}\n"
#                           f"    max_buy: {(max_buy*quantity):,}\n")
#
#         await matcher.finish(print_str)
#     except KahunaException as e:
#         await matcher.finish(e.message)
#
# @kahuna_cmd_ojita.handle()
# @kahuna_cmd_ofrt.handle()
# async def kahuna_cmd_price_func(matcher: Matcher, event: Event, args: Message = CommandArg(), raw_command: str =RawCommand()):
#     # # debug info
#     args_text, user_qq = kahuna_debug_info(event, args, raw_command)
#
#     # help info
#     HELP = ROUGE_PRICE_HELP
#
#     if " * " in args_text:
#         item_name, quantity = args_text.split(" * ", maxsplit=1)
#         quantity = int(quantity)
#     else:
#         item_name, quantity = args_text, 1
#
#     if raw_command == ".ojita":
#         market_location = "jita"
#     elif raw_command == ".ofrt":
#         market_location = "frt"
#     else:
#         await kahuna_cmd_ojita.finish(HELP)
#
#     await kahuna_cmd_price(matcher, event, item_name, quantity, market_location)

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

