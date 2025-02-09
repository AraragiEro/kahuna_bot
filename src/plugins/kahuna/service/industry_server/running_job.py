from tqdm import tqdm

from ..database_server.model import IndustryJobs
from ..character_server import CharacterManager
from ..character_server.character import Character
from ..evesso_server.eveesi import characters_character_id_industry_jobs, corporations_corporation_id_industry_jobs
from ..evesso_server.eveutils import find_max_page, get_multipages_result
from ..database_server.connect import db

# kahuna logger
from ..log_server import logger

class RunningJobOwner:
    @classmethod
    def refresh_character_running_job(cls, character: Character):
        character_running_job = characters_character_id_industry_jobs(character.ac_token, character.character_id)
        if not character_running_job:
            return

        for data in character_running_job:
            data['location_id'] = data['station_id']
            data.pop('station_id')
            data.update({'owner_id': character.character_id})
        with db.atomic():
            IndustryJobs.delete().where(IndustryJobs.owner_id == character.character_id).execute()
            IndustryJobs.insert_many(character_running_job).execute()

    @classmethod
    def refresh_corp_running_job(cls, corp_id, character: Character):
        max_page = find_max_page(corporations_corporation_id_industry_jobs, character.ac_token, corp_id,
                                 begin_page=0, interval=2)
        logger.info("请求资产。")
        results = get_multipages_result(corporations_corporation_id_industry_jobs, max_page, character.ac_token, corp_id)

        with db.atomic():
            IndustryJobs.delete().where(IndustryJobs.owner_id == corp_id).execute()
            with tqdm(total=len(results), desc="写入数据库", unit="page") as pbar:
                for result in results:
                    for jobs in result:
                        jobs.update({'owner_id': corp_id})
                    IndustryJobs.insert_many(result).execute()