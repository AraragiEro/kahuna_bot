from pydantic import BaseModel
from datetime import datetime, timedelta

from ..database_server.model import User as M_User

class User(BaseModel):
    qq: int
    create_date: datetime
    expire_date: datetime
    character_list: list = []

    def get_from_db(self):
        return M_User.get_or_none(M_User.user_qq == self.qq)

    def init_time(self):
        self.create_date = datetime.now()
        self.expire_date = datetime.now()

    def insert_to_db(self):
        user_obj = M_User.get_or_none(M_User.user_qq == self.qq)
        if not user_obj:
            user_obj = M_User()

        user_obj.user_qq = self.qq
        user_obj.create_date = self.create_date
        user_obj.expire_date = self.expire_date

        user_obj.save()

    @property
    def info(self):
        return (f"用户:{self.qq}\n"
                f"创建时间:{self.create_date}\n"
                f"到期时间:{self.expire_date}\n"
                f"剩余时间:{max(timedelta(), self.expire_date - datetime.now())}")

    @property
    def member_status(self):
        return self.expire_date > datetime.now()

    def add_member_time(self, day: int):
        add_time = timedelta(days=day)

        self.expire_date = max(self.expire_date, datetime.now()) + add_time
        self.insert_to_db()
        return self.expire_date

    def clean_member_time(self):
        self.expire_date = datetime.now()
        self.insert_to_db()

    def delete(self):
        user_obj = M_User.get_or_none(self.qq)
        if not user_obj:
            return

        user_obj.delete().execute()