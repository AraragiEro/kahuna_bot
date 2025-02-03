# python model
from typing import Tuple
import traceback
from datetime import datetime

# nonebot model
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg, RawCommand, Command
from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher
from nonebot import on_command
from nonebot.rule import to_me

# permission checker
from ..permission_checker import PermissionChecker

# kahuna model
from .utils import kahuna_debug_info
from ..service.user_server import UserManager

# import Exception
from ..utils import KahunaException

# import logger
from ..service.log_server import logger

# 用户管理器，超级用户限定
user_manager = on_command("user",
                          aliases={
                              ("user", "createUser"),
                              ("user", "addMemberTime"),
                              ("user", "clearMemberTime"),
                              ("user", "deleteUser"),
                          },
                          permission=PermissionChecker.admin,
                          rule=to_me(),
                          priority=10, block=True)
# 用户查询自己信息
user_checkself = on_command("selfinfo", rule=to_me(), priority=10, block=True, permission=PermissionChecker.admin)
# 用户注册
user_sign = on_command("sign", rule=to_me(), priority=10, block=True)

@user_manager.handle()
async def user_manager_func(
        matcher: Matcher,
        event: Event,
        args: Message = CommandArg(),
        cmd: tuple[str, ...] = Command(),
        raw_command: str = RawCommand()
    ):
    HELP = """USAGE:
user.createUser [qq]
user.addMemberTime [qq] [day]
user.clearMemberTime [qq]
user.deleteUser [qq]
"""
    # debug info
    args_text, user_qq = kahuna_debug_info(event, args, raw_command)

    logger.debug(cmd)
    if len(cmd) != 2:
        await matcher.finish(HELP)

    args_list = args_text.split(" ")
    try:
        qq = int(args_list[0])
        _, action = cmd
        if action == "createUser":
            user = UserManager.create_user(qq)
            await matcher.send(user.info)
        elif action == "addMemberTime":
            time_day = int(args_list[1])
            expire_date = UserManager.add_member_time(qq, time_day)
            await matcher.finish(f"用户: {qq} 已添加 {time_day} 天。\n"
                                 f"当前剩余时间：{expire_date - datetime.now()}")
        elif action == "deleteUser":
            UserManager.delete_user(qq)
            await matcher.finish("执行完成。")
        elif action == "clearMemberTime":
            UserManager.clean_member_time(qq)
            await matcher.finish(f"用户 {qq} 时间已清零")
        else:
            await matcher.finish(HELP)
    except KahunaException as e:
        matcher.finish(e.message)
    except IndexError as e:
        logger.error(traceback.format_exc())

@user_checkself.handle()
async def user_checkself_func(matcher: Matcher,
                              event: Event,
                              args: Message = CommandArg(),
                              raw_command: str = RawCommand(),
                              cmd: Tuple = Command()):
    # debug info
    args_list, user_qq = kahuna_debug_info(event, args, raw_command)

    try:
        user = UserManager.get_user(user_qq)
        await matcher.finish(user.info)

    except KahunaException as e:
        await matcher.finish(e.message)

@user_sign.handle()
async def sign_func(
        matcher: Matcher,
        event: Event,
        args: Message = CommandArg(),
        cmd: tuple[str, ...] = Command(),
        raw_command: str = RawCommand()
    ):
    # debug info
    args_text, user_qq = kahuna_debug_info(event, args, raw_command)

    user_obj = UserManager.create_user(user_qq)

    await matcher.send(user_obj.info)

