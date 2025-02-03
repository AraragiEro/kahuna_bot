from oauthlib.oauth2 import InvalidClientIdError
from pydantic import BaseModel
from datetime import datetime

from ..database_server.model import Character as M_Character
from ..evesso_server.oauth import refresh_token
from ...utils import KahunaException


class Character(BaseModel):
    character_id: int
    character_name: str
    QQ: int
    create_date: datetime
    token: str
    refresh_token: str
    expires_date: datetime

    @staticmethod
    def get_all_characters():
        return M_Character.select()

    def get_from_db(self):
        return M_Character.get_or_none(M_Character.character_id == self.character_id)

    def insert_to_db(self):
        obj = self.get_from_db()
        if not obj:
            obj = M_Character()

        obj.character_id = self.character_id
        obj.character_name = self.character_name
        obj.QQ = self.QQ
        obj.create_date = self.create_date
        obj.token = self.token
        obj.refresh_token = self.refresh_token
        obj.expires_date = self.expires_date

        obj.save()

    def refresh_character_token(self):
        try:
            refresh_res_dict = refresh_token(self.refresh_token)
        except InvalidClientIdError as e:
            self.character_id = False
            self.insert_to_db()
            raise KahunaException("refresh token已失效，请重新授权。")
        if refresh_res_dict:
            self.token = refresh_res_dict['access_token']
            self.refresh_token = refresh_res_dict['refresh_token']
            self.expires_date = datetime.fromtimestamp(refresh_res_dict['expires_at'])

        self.insert_to_db()

    @property
    def ac_token(self):
        if not self.token_avaliable:
            self.refresh_character_token()
        return self.token

    @property
    def token_avaliable(self):
        return self.expires_date > datetime.now()

    @property
    def info(self):
        return f"角色:{self.character_name}\n"\
                f"所属用户:{self.QQ}\n"\
                f"角色id:{self.character_id}\n"\
                f"token过期时间:{self.expires_date}\n"

