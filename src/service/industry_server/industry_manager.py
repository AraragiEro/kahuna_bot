

from .running_job import RunningJobOwner
from .system_cost import SystemCost
from ..character_server import CharacterManager
from ..database_server.model import (IndustryJobsCache as M_IndustryJobsCache, IndustryJobs as M_IndustryJobs,
                                     SystemCost as M_SystemCost, SystemCostCache as M_SystemCostCache)
from ..database_server.connect import db

# kahuna logger
from ..log_server import logger


class IndustryManager:
    @classmethod
    def refresh_running_status(cls):
        character_list = [character for character in CharacterManager.character_dict.values()]

        corp_list_id_list = []
        exist_corp_set = set()
        for character in character_list:
            if character.director and character.corp_id not in exist_corp_set:
                corp_list_id_list.append((character.corp_id, character))
                exist_corp_set.add(character.corp_id)

        for character in character_list:
            RunningJobOwner.refresh_character_running_job(character)
        for corp_id, character in corp_list_id_list:
            RunningJobOwner.refresh_corp_running_job(corp_id, character)

        M_IndustryJobsCache.delete().execute()
        db.execute_sql(f"INSERT INTO {M_IndustryJobsCache._meta.table_name} SELECT * FROM {M_IndustryJobs._meta.table_name}")
        logger.info("copy data to cache complete")

    @classmethod
    def refresh_system_cost(cls):
        SystemCost.refresh_system_cost()
        M_SystemCostCache.delete().execute()
        db.execute_sql(
            f"INSERT INTO {M_SystemCostCache._meta.table_name} SELECT * FROM {M_SystemCost._meta.table_name}")
        logger.info("copy data to cache complete")
