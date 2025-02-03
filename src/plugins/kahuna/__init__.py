import os
if os.environ.get('TEST') != '1':
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

    from .service.industry_server.item import get_id_by_name, get_name_by_id
    from .service.industry_server.blueprint_analyse import get_bp_materials

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
    from .event.user import user_manager
    from .event.industry import kahuna_cmd_asset

    t2 = on_command("t2", rule=to_me(), priority=10, block=True)
    @t2.handle()
    async def _(args: Message = CommandArg()):
        args_list = args.extract_plain_text()
        ship_name = args_list
        logger.debug(f"ship_name: {ship_name}")
        typeid = get_id_by_name(ship_name)
        logger.debug(f"typeid: {typeid}")
        mater = get_bp_materials(typeid)
        res = {
            get_name_by_id(type_id): mater_quantity for type_id, mater_quantity in mater.items()
        }
        await t2.send(f"{ship_name}需要以下材料:\n" + json.dumps(res, indent=2, cls=DateTimeEncoder))

    kahuna_cmd_db = on_command("db", rule=to_me(), priority=10, block=True)
    @kahuna_cmd_db.handle()
    async def _(args: Message = CommandArg()):
        HELP = ("db cmd use: db [args] ..."
                "   args:"
                "       1. ls: list all table."
                "       2. drop [table_name]: drop_table")
        args_list = args.extract_plain_text().split(" ")
        main_arg = args_list[0]

        if main_arg == "drop" and len(args_list) > 1:
            if args_list[1] == "all":
                drop_all_table()
            else:
                remain_tables = drop_table(args_list[1])
            await kahuna_cmd_db.send(f"删除完成，剩余表:\n{remain_tables}")
        elif main_arg == "ls":
            await kahuna_cmd_db.send("\n".join(get_tables()))
        elif main_arg == "create":
            create_default_table()
        else:
            await kahuna_cmd_db.send(f"指令错误。\n{HELP}")

    kahuna_cmd_character = on_command("character", rule=to_me(), priority=10, block=True)
    @kahuna_cmd_character.handle()
    async def character_func(matcher: Matcher, event: Event, args: Message = CommandArg()):
        HELP = "character指令:\n"\
               "   add: 获取认证链接。\n"\
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
                                                     "/character add {链接}")
                elif args_list[1].startswith(""):
                    at, rt, et = get_token(args_list[1])
                    character_info = CharacterManager.create_new_character([at, rt, et], user_qq)
                    await kahuna_cmd_character.finish("绑定成功，信息已写入。"
                                         f"{json.dumps(character_info, indent=2, cls=DateTimeEncoder)}")
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

    kahuna_cmd_bp = on_command("bp", rule=to_me(), priority=10, block=True)
    @kahuna_cmd_bp.handle()
    async def kahuna_cmd_bp_func(matcher: Matcher, event: Event, args: Message = CommandArg()):
        HELP = "bp:\n"\
               "   count [物品] [数量]: 获得材料报表。\n"

        args_list = args.extract_plain_text().split(" ")
        logger.debug(args_list is None)
        user_qq = int(event.get_user_id())
        bpa = BpAnalyser()
        try:
            if args_list[0] == "count" and len(args_list) == 3:
                product = args_list[1]
                quantity = int(args_list[2])
                material_dict = bpa.get_product_ori_materials(product, quantity)
                res = f"{product} x {quantity} 清单:\n"
                for material_id, quantity in material_dict.items():
                    res += f"{get_name_by_id(material_id)} {quantity}\n"
                await kahuna_cmd_bp.finish(res)
            else:
                await kahuna_cmd_bp.finish(HELP)
        except KahunaException as e:
            await kahuna_cmd_character.finish(e.message)
