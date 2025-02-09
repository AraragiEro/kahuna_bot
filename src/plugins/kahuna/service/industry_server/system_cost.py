
from ..database_server.model import SystemCost as M_SystemCost
from ..character_server import CharacterManager
from ..character_server.character import Character
from ..evesso_server.eveesi import industry_systems
from ..evesso_server.eveutils import find_max_page, get_multipages_result
from ..database_server.connect import db
from ...utils import chunks

# kahuna logger
from ..log_server import logger


class SystemCost:
    @classmethod
    def refresh_system_cost(cls):
        result = industry_systems()

        insert_data = []
        for item in result:
            data = {"solar_system_id": item["solar_system_id"]}
            for cost in item["cost_indices"]:
                data[cost["activity"]] = cost["cost_index"]
            insert_data.append(data)

        with db.atomic():
            M_SystemCost.delete().execute()
            for chunk in chunks(insert_data, 1000):
                M_SystemCost.insert_many(chunk).execute()