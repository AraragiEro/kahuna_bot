import json

# nonebot model
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand, Command

# kahuna model
from .utils import kahuna_debug_info
from ..service.asset_server import AssetManager
from ..service.character_server import CharacterManager
from ..service.evesso_server.eveesi import characters_character
from ..service.market_server import MarketManager
from ..service.asset_server import AssetContainer
from ..service.evesso_server.oauth import get_auth_url, get_token
from ..service.evesso_server.eveutils import DateTimeEncoder

# kahuna Permission
from ..permission_checker import PermissionChecker
from ..rule_checker import RuleChecker
# import Exception
from ..utils import KahunaException

# import logger
from ..service.log_server import logger

kahuna_cmd_character = on_command("character", rule=PermissionChecker.member, priority=10, block=True)
@kahuna_cmd_character.handle()
async def character_func(matcher: Matcher, event: Event, args: Message = CommandArg()):
    HELP = "character指令:\n" \
           "   add: 获取认证链接。\n" \
           "   (私聊)add [认证返回链接]: 添加角色\n"

    args_list = args.extract_plain_text().split(" ")
    logger.debug(args_list is None)
    user_qq = int(event.get_user_id())

    try:
        if args_list[0] == "add":
            if len(args_list) < 2:
                url = get_auth_url()
                await kahuna_cmd_character.finish(f"{url}\n"
                                                  "请点击链接进行认证，在认证完成后页面变为空白时，"
                                                  "将浏览器内的链接复制后按照格式私聊发送给机器人。\n"
                                                  ".character add {链接}")
            elif args_list[1].startswith(""):
                at, rt, et = get_token(args_list[1])
                character_info = CharacterManager.create_new_character([at, rt, et], user_qq)
                print_info = (f"绑定成功，信息已写入。\n"
                              f"角色名：{character_info['character_name']}\n"
                              f"QQ: {character_info['QQ']}\n"
                              f"创建时间：{character_info['create_date']}\n")
                await kahuna_cmd_character.finish(print_info)
        elif args_list[0] == "refresh" and len(args_list) > 1:
            character_id = int(args_list[1])
            character = CharacterManager.refresh_character_token(character_id)
            await kahuna_cmd_character.finish(f"角色 {character.character_name} token已刷新。\n"
                                              f"到期时间：{character.expires_date}")
        elif args_list[0] == "ls":
            res_str = ""
            character_list = CharacterManager.get_user_all_characters(user_qq)
            for character in character_list:
                res_str += character.info
                res_str += "\n"
            await kahuna_cmd_character.finish(res_str)
        else:
            await kahuna_cmd_character.finish(HELP)
    except KahunaException as e:
        await kahuna_cmd_character.finish(e.message)