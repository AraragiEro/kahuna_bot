from enum import Enum

# Kahuna model
from ..sde_service.utils import SdeUtils
from ..database_server.model import AssetCache
from ..database_server.model import AssetContainer as M_AssetContainer
from ..evesso_server.eveesi import universe_structures_structure, universe_stations_station
from ..character_server import CharacterManager
from ..user_server import UserManager
from ..sde_service.database import MapSolarSystems

class ContainerTag(Enum):
    bp = 'blueprint'
    reac = 'reaction'
    manu = 'manufacturing'

class AssetContainer:
    asset_location_id = 0
    asset_location_type = 0
    asset_name = 0
    asset_owner_qq = 0
    structure_id = 0
    solar_system_id = 0
    asset_owner_id = 0
    asset_owner_type = 0
    tag = None

    def __init__(self, asset_location_id: int, asset_location_type: str, asset_name: str, asset_owner_qq: int):
        self.asset_location_id = asset_location_id
        self.asset_location_type = asset_location_type
        self.asset_name = asset_name
        self.asset_owner_qq = asset_owner_qq

    @classmethod
    def get_all_asset_container(cls):
        return M_AssetContainer.select()

    @classmethod
    def operater_has_container_permission(cls, operate_qq: int, owner_id: int):
        operate_qq_list = CharacterManager.get_user_all_characters(operate_qq)
        for character in operate_qq_list:
            if (owner_id == character.character_id and operate_qq == character.QQ) or \
               (owner_id == character.corp_id and operate_qq == character.QQ):
                return True
        return False

    @classmethod
    def find_secret_data(cls, secret_type: str) -> list:
        item_id = SdeUtils.get_id_by_name(secret_type)
        if not item_id:
            return []

        result = AssetCache.select().where(
            (AssetCache.type_id == item_id))
        find_list = [data for data in result]
        return find_list


    @classmethod
    def find_type_structure(cls, location_id, location_flag):
        """
        根据提供的location_id在AssetCache中进行查询，目标是找到一个顶层的location。
        顶层的location符合如下特征之一：
        1. location_type=="station", 则该条数据的location_id是顶层location
        2. location_type=="solar_system", 则该条数据的item_id是顶层location
        """
        if_station_data = AssetCache.get_or_none(AssetCache.location_id == location_id, AssetCache.location_type == "station")
        if if_station_data:
            return if_station_data.location_id, if_station_data.location_flag

        if_structure_data = AssetCache.get_or_none(AssetCache.item_id == location_id, AssetCache.location_type == "solar_system")
        if if_structure_data:
            return if_structure_data.item_id, if_structure_data.location_flag

        father_data = AssetCache.get_or_none(AssetCache.item_id == location_id)
        if father_data:
            return cls.find_type_structure(father_data.location_id, father_data.location_type)
        return location_id, location_flag

    @classmethod
    def find_container(cls, secret_type: str, operate_qq: int):
        # 1. 获取数据
        # 在asset_cache找到type_id==get_id_by_name(secret_type) and quantity==secret_quantity的条目
        secret_data_list = cls.find_secret_data(secret_type)

        count_dict = {}
        for data in secret_data_list:
            if (data.location_id, data.location_flag, data.owner_id) not in count_dict:
                count_dict[(data.location_id, data.location_flag, data.owner_id)] = 0
            count_dict[(data.location_id, data.location_flag, data.owner_id)] += data.quantity
        count_list = [(*key, value) for key, value in count_dict.items()]

        verified_container = []
        # 2. 权限校验
        for data in count_list:
            if cls.operater_has_container_permission(operate_qq, data[2]):
                verified_container.append(data)

        container_data = []
        for data in verified_container:
            # 找到secret物品所在建筑
            structure_id, structure_flag = cls.find_type_structure(data[0], data[1])
            if structure_id and structure_flag:
                container_data.append((data[0], data[1], structure_id, data[3]))

        access_character = CharacterManager.get_character_by_id(UserManager.get_main_character_id(operate_qq))
        container_info = []
        for data in container_data:
            info = cls.get_structure_info(access_character.ac_token, data[2])
            info.update({
                'location_id': data[0],
                'location_flag': data[1],
                'structure_type': get_name_by_id(info['type_id']),
                'exist_quantity': data[3],

            })
            if info:
                container_info.append(info)

        return container_info

    @classmethod
    def get_structure_info(cls, ac_token: str, structure_id: int) -> dict:
        """
        'name' = {str} '4-HWWF - WinterCo. Central Station'
        'owner_id' = {int} 98599770
        'position' = {dict: 3} {'x': -439918627801.0, 'y': -86578525155.0, 'z': -1177327092030.0}
        'solar_system_id' = {int} 30000240
        'type_id' = {int} 35834
        """
        info = universe_stations_station(structure_id) if len(str(structure_id)) <= 8 else universe_structures_structure(ac_token, structure_id)
        info.update({
            'system': MapSolarSystems.get(MapSolarSystems.solarSystemID==info[('system_id') if len(str(structure_id)) <= 8 else 'solar_system_id'])
                                     .solarSystemName
        })
        return info


    def get_from_db(self):
        return M_AssetContainer.get_or_none(
            (M_AssetContainer.asset_location_id == self.asset_location_id) &
            (M_AssetContainer.asset_location_type == self.asset_location_type))

    def insert_to_db(self):
        obj = self.get_from_db()
        if not obj:
            obj = M_AssetContainer()

        """
        asset_location_id = IntegerField()
        asset_location_type = CharField()
        solar_system_id = IntegerField()
        asset_name = TextField()
        asset_owner_id = IntegerField()
        asset_owner_type = CharField()
        asset_owner_qq = IntegerField()
        """
        obj.asset_location_id = self.asset_location_id
        obj.asset_location_type = self.asset_location_type
        obj.structure_id = self.structure_id
        obj.solar_system_id = self.solar_system_id
        obj.asset_name = self.asset_name
        obj.asset_owner_id = self.asset_owner_id
        obj.asset_owner_type = self.asset_owner_type
        obj.asset_owner_qq = self.asset_owner_qq
        obj.tag = self.tag

        obj.save()

    @classmethod
    def get_location_id_by_qq_tag(cls, qq: int, tag: str) -> list[int]:
        return [container.asset_location_id for container in
                M_AssetContainer.select().where(M_AssetContainer.asset_owner_qq == qq, M_AssetContainer.tag == tag)]

    def __str__(self):
        return (f"id: {self.asset_location_id}\n"
                f"name: {self.asset_name}\n"
                f"所属用户: {self.asset_owner_qq}\n")


