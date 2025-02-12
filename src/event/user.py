from datetime import datetime

# import logger
from astrbot.api import logger

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register

# kahuna model
from .utils import kahuna_debug_info
from ..service.user_server import UserManager

# import Exception
from ..utils import KahunaException

class UserEvent():
    @staticmethod
    def create(event: AstrMessageEvent, user_qq: int):
        return event.plain_result(UserManager.create_user(user_qq).info)

    @staticmethod
    def addMemberTime(event: AstrMessageEvent, user_qq: int, time_day: int):
        expire_date = UserManager.add_member_time(user_qq, time_day)
        return event.plain_result(f"用户: {user_qq} 已添加 {time_day} 天。\n"
                                  f"当前剩余时间：{expire_date - datetime.now()}")

    @staticmethod
    def deleteUser(event: AstrMessageEvent, user_qq: int):
        UserManager.delete_user(user_qq)
        return event.plain_result("执行完成。")

    @staticmethod
    def clearMemberTime(event: AstrMessageEvent, user_qq: int):
        UserManager.clean_member_time(user_qq)
        return event.plain_result(f"用户 {user_qq} 时间已清零")

    @staticmethod
    def self_info(event: AstrMessageEvent):
        user = UserManager.get_user(int(event.get_sender_id()))
        return event.plain_result(user.info)

    @staticmethod
    def setMainCharacter(event: AstrMessageEvent, main_character: str):
        user_qq = int(event.get_sender_id())
        UserManager.set_main_character(user_qq, main_character)
        return event.plain_result("设置主角色 执行完成")

    @staticmethod
    def sign(event: AstrMessageEvent):
        user_qq = int(event.get_sender_id())
        user_obj = UserManager.create_user(user_qq)
        return event.plain_result(user_obj.info)