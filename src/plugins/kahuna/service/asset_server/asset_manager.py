import time
import threading

from ..database_server.model import (AssetCache as M_AssetCache,
                                                              Asset as M_Asset)
from ..database_server.connect import db
from .asset import Asset
from ..character_server.character_manager import CharacterManager

# kahuna KahunaException
from ...utils import KahunaException

# kahuna logger
from ..log_server import logger



class AssetManager:
    asset_dict: dict[(str, int): Asset] = dict() # {(owner_type, owner_id): Asset}
    monitor_process = None

    @classmethod
    def init_asset_dict(cls):
        owner_list = Asset.get_all_asset_owner()
        for owner in owner_list:
            access_character = CharacterManager.get_character_by_id(owner.asset_access_character_id)
            asset = Asset(
                owner.asset_owner_qq,
                owner.asset_type,
                owner.asset_owner_id,
                access_character)
            cls.asset_dict[(asset.owner_type, asset.owner_id)] = asset
        cls.monitor_process = threading.Thread(target=cls.asset_monior_process).start()

    @classmethod
    def create_asset(cls, qq_id: int, type: str, owner_id, character_obj):
        asset = Asset(qq_id, type, owner_id, character_obj)
        if not asset.token_accessable:
            return

        asset.insert_to_db()
        cls.asset_dict[(type, owner_id)] = asset
        return asset

    @classmethod
    def copy_to_cache(cls):
        with db.atomic():
            M_AssetCache.delete().execute()
            db.execute_sql(f"INSERT INTO {M_AssetCache._meta.table_name} SELECT * FROM {M_Asset._meta.table_name}")
            logger.info("copy data to cache complete")

    @classmethod
    def refresh_asset(cls, type, owner_id):
        asset: Asset = cls.asset_dict.get((type, owner_id), None)
        if asset is None:
            raise KahunaException("没有找到对应的库存。")
        asset.delete_asset()
        asset.get_asset()
        cls.copy_to_cache()
        return asset

    @classmethod
    def asset_monior_process(cls):
        time.sleep(60 * 5)
        while True:
            for asset in cls.asset_dict.values():
                asset.get_asset()
            cls.copy_to_cache()
            time.sleep(60 * 15)

AssetManager.init_asset_dict()

