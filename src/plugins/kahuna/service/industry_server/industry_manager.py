import os
if os.environ.get('KAHUNA_BOT_TEST') != '1':
    from nonebot import require
    require("nonebot_plugin_apscheduler")
    from nonebot_plugin_apscheduler import scheduler


from .running_job import RunningJobOwner
from ..character_server import CharacterManager
from ..database_server.model import IndustryJobsCache as M_IndustryJobsCache, IndustryJobs as M_IndustryJobs
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

if os.environ.get('KAHUNA_BOT_TEST') != '1':
    scheduler.add_job(IndustryManager.refresh_running_status, "interval", minutes=5)

