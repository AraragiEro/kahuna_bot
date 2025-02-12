import json

# import logger
from astrbot.api import logger

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register

# # kahuna model
from .utils import kahuna_debug_info
# from ..service.asset_server import AssetManager
from ..service.character_server import CharacterManager
# from ..service.evesso_server.eveesi import characters_character
# from ..service.market_server import MarketManager
# from ..service.asset_server import AssetContainer
from ..service.evesso_server.oauth import get_auth_url, get_token
# from ..service.evesso_server.eveutils import DateTimeEncoder

# # kahuna Permission
# from ..permission_checker import PermissionChecker
# from ..rule_checker import RuleChecker
# # import Exception
# from ..utils import KahunaException



class CharacterEvent():
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @staticmethod
    def auth(event: AstrMessageEvent):
        kahuna_debug_info(event)

        return event.plain_result(get_auth_url())

    @staticmethod
    def add(event: AstrMessageEvent, back_url):
        user_qq = kahuna_debug_info(event)
        at, rt, et = get_token(back_url)
        character_info = CharacterManager.create_new_character([at, rt, et], user_qq)
        print_info = (f"绑定成功，信息已写入。\n"
                      f"角色名：{character_info['character_name']}\n"
                      f"QQ: {character_info['QQ']}\n"
                      f"创建时间：{character_info['create_date']}\n")
        logger.info(4)
        return event.plain_result(print_info)