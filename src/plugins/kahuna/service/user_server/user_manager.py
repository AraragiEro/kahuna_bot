from datetime import datetime
from cachetools import TTLCache

from .user import User
from ..database_server.model import User as M_User

# import Exception
from ...utils import KahunaException

ESI_CACHE = TTLCache(maxsize=100, ttl=300)

class UserManager:
    user_dict = dict() # {qq_id: User()}

    @classmethod
    def init_user_list(cls):
        user_list = M_User.select()
        for user in user_list:
            usr_obj = User(
                qq=user.user_qq,
                create_date=user.create_date,
                expire_date=user.expire_date
            )
            cls.user_dict[usr_obj.qq] = usr_obj

    @classmethod
    def create_user(cls, qq: int) -> User:
        if (user := cls.user_dict.get(qq, None)) is None:
            user = User(qq=qq, create_date=datetime.now(), expire_date=datetime.now())
        user.init_time()
        user.insert_to_db()
        cls.user_dict[user.qq] = user

        return user

    @classmethod
    def get_user(cls, qq: int):
        if (user := cls.user_dict.get(qq, None)) is None:
            raise KahunaException("用户不存在。")
        return user

    @classmethod
    def add_member_time(cls, qq: int, days: int):
        if (user := cls.user_dict.get(qq, None)) is None:
            raise KahunaException("用户不存在。")
        return user.add_member_time(days)

    @classmethod
    def delete_user(cls, qq: int):
        if (user := cls.user_dict.get(qq, None)) is None:
            return
        user.delete()
        cls.user_dict.pop(qq)

    @classmethod
    def clean_member_time(cls, qq: int):
        if (user := cls.user_dict.get(qq, None)) is None:
            raise KahunaException("用户不存在。")
        user.clean_member_time()

UserManager.init_user_list()