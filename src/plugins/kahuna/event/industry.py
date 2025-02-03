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
# kahuna Permission
from ..permission_checker import PermissionChecker
from ..rule_checker import RuleChecker
# import Exception
from ..utils import KahunaException

# import logger

# 资产类指令
kahuna_cmd_asset = on_command(
    "asset",
    aliases={
        ("asset", "owner", "add"),
        ("asset", "owner", "del"),
        ("asset", "owner", "refresh"),
        ("asset", "container", "add"),
        ("asset", "container", "del")
    },
    permission=PermissionChecker.admin,
    priority=10, block=True)

@kahuna_cmd_asset.handle()
async def _(matcher: Matcher,
        event: Event,
        args: Message = CommandArg(),
        raw_cmd: str = RawCommand(),
        cmd: tuple[str, ...] = Command()
    ):

    # debug info
    args_text, user_qq = kahuna_debug_info(event, args, raw_cmd)

    HELP = """USAGE:
.asset.owner.add character [character_name]
.asset.owner.add corp [character_name]
    """

    try:
        if len(cmd) == 3 and cmd[0:2] == ("asset", "owner"):
            args_list = args_text.split(" ")
            owner_type = args_list[0]
            character_name = " ".join(args_list[1:])
            character = CharacterManager.get_character_by_name_qq(character_name, user_qq)
            # 如果是corp，需要通过character拿到corpid
            if owner_type == "corp":
                character_info = characters_character(character.character_id)
                owner_id = int(character_info["corporation_id"])
            elif owner_type == "character":
                owner_id = character.character_id
            else:
                await matcher.finish(HELP)
            if cmd[3] == "add":
                asset = AssetManager.create_asset(user_qq, owner_type, owner_id, character)
                await matcher.finish(f"库存已成功创建。\n"
                                     f"库存条目 {asset.asset_item_count}")
            elif cmd[3] == "refresh":
                asset = AssetManager.refresh_asset(owner_type, owner_id)

        else:
            await matcher.finish(HELP)
    except KahunaException as err:
        await matcher.finish(err)