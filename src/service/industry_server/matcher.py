import json

from ..database_server.model import Matcher as M_Matcher

MATCHER_KEY = ["bp", "market_group", "group", "meta", "category"]

class Matcher:
    matcher_name = ""
    user_qq = 0
    matcher_type = ""
    matcher_data = {matcher_k: dict() for matcher_k in MATCHER_KEY}

    def __init__(self, matcher_name, user_qq, matcher_type):
        self.matcher_name = matcher_name
        self.user_qq = user_qq
        self.matcher_type = matcher_type

    @classmethod
    def init_from_db_data(cls, data: M_Matcher):
        matcher = Matcher(data.matcher_name, data.user_qq, data.matcher_type)
        matcher.matcher_data = json.loads(data.matcher_data)

        return matcher

    def get_from_db(self):
        return M_Matcher.get_or_none(M_Matcher.matcher_name == self.matcher_name)

    def insert_to_db(self):
        obj = self.get_from_db()
        if not obj:
            obj = M_Matcher()

        obj.matcher_name = self.matcher_name
        obj.user_qq = self.user_qq
        obj.matcher_type = self.matcher_type
        obj.matcher_data = json.dumps(self.matcher_data)

        obj.save()

    def delete_from_db(self):
        M_Matcher.delete().where(M_Matcher.matcher_name == self.matcher_name).execute()
