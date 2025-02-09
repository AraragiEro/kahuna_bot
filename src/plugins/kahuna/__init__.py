import os
if os.environ.get('KAHUNA_BOT_TEST') != '1':
    import json

    from nonebot import get_plugin_config
    from nonebot.plugin import PluginMetadata
    from nonebot import on_command
    from nonebot.rule import to_me
    from nonebot.adapters.onebot.v11 import Message
    from nonebot.params import CommandArg
    from nonebot.adapters.onebot.v11 import Event
    from nonebot.matcher import Matcher
    from .config import Config

    __plugin_meta__ = PluginMetadata(
        name="kahuna",
        description="",
        usage="",
        config=Config,
    )

    config = get_plugin_config(Config)
    os.environ["KAHUNA_DB_DIR"] = config.db_dir

    # --------------------------------
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    from .service.evesso_server.oauth import get_auth_url, get_token
    from .service.evesso_server.eveutils import DateTimeEncoder
    from .service.database_server import drop_table, get_tables, create_default_table, drop_all_table

    from .service.sde_service.utils import get_id_by_name, get_name_by_id
    from .service.industry_server.blueprint_analyse import BPManager

    from .service.user_server.user_manager import UserManager
    from .service.character_server.character_manager import CharacterManager
    from .service.industry_server.blueprint_analyse import BpAnalyser

    # 估价服务

    # 测试
    from .event.test import test_event

    from .utils import KahunaException

    # import logger
    from .service.log_server import logger

    # import event
    from .event.utils import kahuna_debug_info
    from .event.price import kahuna_cmd_ojita
    from .event.user import user_manager, kahuna_cmd_user_sign
    from .event.industry import kahuna_cmd_asset
    from .event.chat import kahuna_cmd_chat
    from .event.character import kahuna_cmd_character

    # t2 = on_command("t2", rule=to_me(), priority=10, block=True)
    # @t2.handle()
    # async def _(args: Message = CommandArg()):
    #     args_list = args.extract_plain_text()
    #     ship_name = args_list
    #     logger.debug(f"ship_name: {ship_name}")
    #     typeid = get_id_by_name(ship_name)
    #     logger.debug(f"typeid: {typeid}")
    #     mater = get_bp_materials(typeid)
    #     res = {
    #         get_name_by_id(type_id): mater_quantity for type_id, mater_quantity in mater.items()
    #     }
    #     await t2.send(f"{ship_name}需要以下材料:\n" + json.dumps(res, indent=2, cls=DateTimeEncoder))

    # kahuna_cmd_db = on_command("db", rule=to_me(), priority=10, block=True)
    # @kahuna_cmd_db.handle()
    # async def _(args: Message = CommandArg()):
    #     HELP = ("db cmd use: db [args] ..."
    #             "   args:"
    #             "       1. ls: list all table."
    #             "       2. drop [table_name]: drop_table")
    #     args_list = args.extract_plain_text().split(" ")
    #     main_arg = args_list[0]
    #
    #     if main_arg == "drop" and len(args_list) > 1:
    #         if args_list[1] == "all":
    #             drop_all_table()
    #         else:
    #             remain_tables = drop_table(args_list[1])
    #         await kahuna_cmd_db.send(f"删除完成，剩余表:\n{remain_tables}")
    #     elif main_arg == "ls":
    #         await kahuna_cmd_db.send("\n".join(get_tables()))
    #     elif main_arg == "create":
    #         create_default_table()
    #     else:
    #         await kahuna_cmd_db.send(f"指令错误。\n{HELP}")

    # kahuna_cmd_bp = on_command("bp", rule=to_me(), priority=10, block=True)
    # @kahuna_cmd_bp.handle()
    # async def kahuna_cmd_bp_func(matcher: Matcher, event: Event, args: Message = CommandArg()):
    #     HELP = "bp:\n"\
    #            "   count [物品] [数量]: 获得材料报表。\n"
    #
    #     args_list = args.extract_plain_text().split(" ")
    #     logger.debug(args_list is None)
    #     user_qq = int(event.get_user_id())
    #     bpa = BpAnalyser()
    #     try:
    #         if args_list[0] == "count" and len(args_list) == 3:
    #             product = args_list[1]
    #             quantity = int(args_list[2])
    #             material_dict = bpa.get_product_ori_materials(product, quantity)
    #             res = f"{product} x {quantity} 清单:\n"
    #             for material_id, quantity in material_dict.items():
    #                 res += f"{get_name_by_id(material_id)} {quantity}\n"
    #             await kahuna_cmd_bp.finish(res)
    #         else:
    #             await kahuna_cmd_bp.finish(HELP)
    #     except KahunaException as e:
    #         await kahuna_cmd_character.finish(e.message)
