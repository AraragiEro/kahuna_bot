
import time
from datetime import datetime
from peewee import chunked

from .asset_container import AssetContainer, ContainerTag
from ..database_server.model import (AssetCache as M_AssetCache, Asset as M_Asset,
                                     BlueprintAsset as M_BlueprintAsset, BlueprintAssetCache as M_BlueprintAssetCache)
from ..database_server.connect import db
from .asset_owner import AssetOwner
from ..character_server.character_manager import CharacterManager
from ..user_server import UserManager
from ..evesso_server.eveesi import universe_structures_structure

# kahuna KahunaException
from ...utils import KahunaException

# kahuna logger
from ..log_server import logger

class AssetManager:
    asset_dict: dict[(str, int): AssetOwner] = dict() # {(owner_type, owner_id): Asset}
    container_dict: dict[(int, str): AssetContainer] = dict() # {(owner_qq, location_id): AssetContainer}
    monitor_process = None
    last_refresh = None

    @classmethod
    def init_asset_dict(cls):
        owner_list = AssetOwner.get_all_asset_owner()
        for owner in owner_list:
            access_character = CharacterManager.get_character_by_id(owner.asset_access_character_id)
            asset_owner = AssetOwner(
                owner.asset_owner_qq,
                owner.asset_type,
                owner.asset_owner_id,
                access_character)
            cls.asset_dict[(asset_owner.owner_type, asset_owner.owner_id)] = asset_owner

    @classmethod
    def init_container_dict(cls):
        container_list = AssetContainer.get_all_asset_container()
        for container in container_list:
            asset_container = AssetContainer(
                container.asset_location_id,
                container.asset_location_type,
                container.asset_name,
                container.asset_owner_qq,
            )
            asset_container.structure_id = container.structure_id
            asset_container.solar_system_id = container.solar_system_id
            asset_container.asset_owner_id = container.asset_owner_id
            asset_container.asset_owner_type = container.asset_owner_type
            asset_container.tag = container.tag

            cls.container_dict[(asset_container.asset_owner_qq, asset_container.asset_location_id)] = asset_container

    @classmethod
    def create_asset(cls, qq_id: int, type: str, owner_id, character_obj):
        asset = AssetOwner(qq_id, type, owner_id, character_obj)
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
        with db.atomic():
            M_BlueprintAssetCache.delete().execute()
            db.execute_sql(f"INSERT INTO {M_BlueprintAssetCache._meta.table_name} SELECT * FROM {M_BlueprintAsset._meta.table_name}")
            logger.info("copy data to cache complete")

    @classmethod
    def refresh_asset(cls, type, owner_id):
        asset: AssetOwner = cls.asset_dict.get((type, owner_id), None)
        if asset is None:
            raise KahunaException("没有找到对应的库存。")
        asset.delete_asset()
        asset.get_asset()
        cls.copy_to_cache()
        return asset

    @classmethod
    def refresh_all_asset(cls):
        for asset in cls.asset_dict.values():
            asset.get_asset()
        cls.copy_to_cache()

    @classmethod
    def add_container(cls, owner_qq: int, location_id: int, location_type: str, asset_name: str, operate_qq: int):
        # 权限校验
        asset_data = M_AssetCache.get_or_none(M_AssetCache.location_id == location_id)
        if not asset_data or not AssetContainer.operater_has_container_permission(operate_qq, asset_data.owner_id):
            raise KahunaException("container permission denied.")

        """
        solar_system_id = 0
        asset_owner_id = 0
        """

        asset_container = AssetContainer(
            location_id,
            location_type,
            asset_name,
            owner_qq
        )

        access_character = CharacterManager.get_character_by_id(UserManager.get_main_character_id(operate_qq))
        structure_id, structure_flag = AssetContainer.find_type_structure(asset_data.location_id, asset_data.location_flag)
        structure_info = universe_structures_structure(access_character.ac_token, structure_id)

        asset_container.asset_owner_id = asset_data.owner_id
        asset_container.asset_owner_type = asset_data.asset_type
        asset_container.structure_id = structure_id
        asset_container.solar_system_id = structure_info["solar_system_id"]

        asset_container.insert_to_db()
        cls.container_dict[(owner_qq, asset_name)] = asset_container

        return asset_container

    @classmethod
    def set_container_tag(cls, require_list: list[int, int], tag: str):
        if tag not in ContainerTag.__members__:
            raise KahunaException("tag must be [bp, reac, manu]")
        success_list = []
        for owner_qq, container_id in require_list:
            if (owner_qq, container_id) not in cls.container_dict:
                continue

            container = cls.container_dict[owner_qq, container_id]
            container.tag = tag
            container.insert_to_db()
            success_list.append(container)
        return success_list


AssetManager.init_asset_dict()
AssetManager.init_container_dict()
