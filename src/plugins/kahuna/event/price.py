# nonebot model
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg, RawCommand
from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher
from nonebot import on_command

# kahuna model
from .utils import kahuna_debug_info
from ..service.market_server import PriceService

# kahuna Permission
from ..permission_checker import PermissionChecker

# import Exception
from ..utils import KahunaException

# import logger
from ..service.log_server import logger

# global value
ROUGE_PRICE_HELP = ("ojita/ofrt:\n" \
                    "   [物品]:       获得估价。\n"
                    "   [物品] * [数量]: 获得估价。\n")

# define event
# 获取jita价格
kahuna_cmd_ofrt = on_command("ofrt",
                             permission=PermissionChecker.default_permission,
                             priority=10, block=True)
# 获取联盟市场价格
kahuna_cmd_ojita = on_command("ojita",
                              permission=PermissionChecker.default_permission,
                              priority=10, block=True)

async def kahuna_cmd_price(matcher: Matcher, event: Event, product_name: str, quantity: int, market_location: str):
    logger.debug("go in cmd price")

    try:
        max_buy, mid_price, min_sell = PriceService.get_price_rouge(product_name, market_location)
        print_str = (f"{product_name} price in {market_location}:\n"
                     f"    min_sell: {min_sell:,}\n"
                     f"    mid_price: {mid_price:,}\n"
                     f"    max_buy: {max_buy:,}\n")
        if quantity > 1:
            print_str += ("\n"
                          f"{quantity} x {product_name}:\n"
                          f"    min_sell: {(min_sell*quantity):,}\n"
                          f"    mid_price: {(mid_price*quantity):,}\n"
                          f"    max_buy: {(max_buy*quantity):,}\n")

        await matcher.finish(print_str)
    except KahunaException as e:
        await matcher.finish(e.message)

@kahuna_cmd_ojita.handle()
@kahuna_cmd_ofrt.handle()
async def kahuna_cmd_price_func(matcher: Matcher, event: Event, args: Message = CommandArg(), raw_command: str =RawCommand()):
    # # debug info
    args_text, user_qq = kahuna_debug_info(event, args, raw_command)

    # help info
    HELP = ROUGE_PRICE_HELP

    if " * " in args_text:
        item_name, quantity = args_text.split(" * ", maxsplit=1)
        quantity = int(quantity)
    else:
        item_name, quantity = args_text, 1

    if raw_command == ".ojita":
        market_location = "jita"
    elif raw_command == ".ofrt":
        market_location = "frt"
    else:
        await kahuna_cmd_ojita.finish(HELP)

    await kahuna_cmd_price(matcher, event, item_name, quantity, market_location)
