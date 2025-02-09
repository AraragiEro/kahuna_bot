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
from ..service.chat_server.chat import chat_once, print_response

# kahuna Permission
from ..permission_checker import PermissionChecker
from ..rule_checker import RuleChecker
# import Exception
from ..utils import KahunaException


# import logger
from ..service.log_server import logger

kahuna_cmd_chat = on_command(
    "chat",
    permission=PermissionChecker.admin,
    priority=10, block=True
)

@kahuna_cmd_chat.handle()
async def _(
    matcher: Matcher,
    event: Event,
    args: Message = CommandArg(),
    raw_cmd: str = RawCommand(),
    cmd: tuple[str, ...] = Command()
):
    # debug info
    args_text, user_qq = kahuna_debug_info(event, args, raw_cmd)

    HELP = """USAGE:
.chat [message]
    """
    try:
        if len(cmd) == 1:
            responce = chat_once(args_text)
            res = print_response(responce)
            await matcher.finish(res)
        else:
            await matcher.finish(HELP)
    except KahunaException as e:
        await matcher.finish(e.message)
