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

# kahuna Permission
from ..permission_checker import PermissionChecker
from ..rule_checker import RuleChecker
# import Exception
from ..utils import KahunaException

# import logger
from ..service.log_server import logger

# 资产类管理员指令
kahuna_cmd_asset = on_command(
    "asset",
    aliases={
        ("asset", "admin"),
        ("asset", "owner", "add"),
        ("asset", "owner", "del"),
        ("asset", "owner", "refresh"),
        ("asset", "container", "add"),
        ("asset", "container", "find")
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
.asset.owner.add (character/corp) (character_name)
.asset.owner.refresh (character/corp) (character_name)
.asset.container.find (secret_type)
.asset.container.add [库存空间id] [库存空间flag] [授权目标qq] [库存空间别名]
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

            if cmd[2] == "add":
                asset = AssetManager.create_asset(user_qq, owner_type, owner_id, character)
                await matcher.finish(f"库存已成功创建。\n"
                                     f"库存条目 {asset.asset_item_count}")
            elif cmd[2] == "refresh":
                asset = AssetManager.refresh_asset(owner_type, owner_id)

        elif len(cmd) == 3 and cmd[0:2] == ("asset", "container"):
            if cmd[2] == 'find':
                secret_type = args_text

                container_info = AssetContainer.find_container(secret_type, user_qq)

                print_info = f"找到{len(container_info)}个符合条件的库存空间。\n"
                for container in container_info:
                    print_info += (f"\n建筑名：{container['name']} 数量：{container['exist_quantity']}\n"
                                   f"建筑类型：{container['structure_type']}\n"
                                   f"星系：{container['system']}\n"
                                   f"添加库存指令：.asset.container.add {container['location_id']} {container['location_flag']} [授权目标qq] [库存空间别名]\n")
                await matcher.finish(print_info)
            if cmd[2] == 'add':
                args_list = args_text.split(" ")
                location_id = int(args_list[0])
                location_flag = args_list[1]
                target_qq = int(args_list[2])
                container_name = " ".join(args_list[3:])

                container = AssetManager.add_container(target_qq, location_id, location_flag, container_name, user_qq)
                print_info = (f"已授权 {target_qq} 使用属于 {user_qq} 的库存: {location_id}。\n")
                await matcher.finish(print_info)

        else:
            await matcher.finish(HELP)
    except KahunaException as err:
        await matcher.finish(err.message)

# 资产类管理员指令
kahuna_cmd_market = on_command(
    "market",
    aliases={
        ("market", "admin"),
        ("market", "order")
    },
    permission=PermissionChecker.admin,
    priority=10, block=True)
@kahuna_cmd_market.handle()
async def _(matcher: Matcher,
        event: Event,
        args: Message = CommandArg(),
        raw_cmd: str = RawCommand(),
        cmd: tuple[str, ...] = Command()
    ):
    # debug info
    args_text, user_qq = kahuna_debug_info(event, args, raw_cmd)

    HELP = """USAGE:
.market.order refresh
    """
    try:
        if len(cmd) == 2 and cmd[0:2] == ("market", "order") and args_text == "refresh":

            res_log = MarketManager.refresh_market()
            await matcher.finish(res_log)
        else:
            await matcher.finish(HELP)
    except KahunaException as e:
        await matcher.finish(e.message)
