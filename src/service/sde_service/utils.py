from functools import lru_cache
import networkx as nx
from thefuzz import fuzz, process
from peewee import DoesNotExist
from cachetools import TTLCache, cached

from ...service.sde_service.database import InvTypes, InvGroups, InvCategories
from ...service.sde_service.database import MetaGroups, MarketGroups
from ..database_server.model import InvTypeMap, AssetCache
from ..database_server.model import MarketPriceCache, SystemCostCache

from .database_cn import InvTypes as InvTypes_zh

en_invtype_name_list = [res.typeName for res in InvTypes.select(InvTypes.typeName).where(InvTypes.marketGroupID != 0)]
zh_invtype_name_list = [res.typeName for res in InvTypes_zh.select(InvTypes_zh.typeName).where(InvTypes_zh.marketGroupID != 0)]



class SdeUtils:
    _market_tree = None
    item_map_dict = dict()

    @classmethod
    def init_type_map(cls):
        cls.item_map_dict = {res.maped_type: res.target_type for res in InvTypeMap.select()}

    @classmethod
    def add_type_map(cls, maped_item: str, target_item: str) -> tuple:
        if maped_item in cls.item_map_dict:
            return False, None
        if not SdeUtils.get_id_by_name(target_item):
            return False, SdeUtils.fuzz_type(target_item)
        new_map = InvTypeMap(maped_item, target_item)
        new_map.save()
        cls.item_map_dict[maped_item] = new_map

    @staticmethod
    @lru_cache(maxsize=2)
    def get_t2_ship() -> list:
        t2_search = (
            InvTypes.select(InvTypes.typeName)
            .join(InvGroups, on=(InvTypes.groupID == InvGroups.groupID))
            .join(InvCategories, on=(InvGroups.categoryID == InvCategories.categoryID))
            .where(InvCategories.categoryName == "Ship")
            .switch(InvTypes)
            .where(InvTypes.marketGroupID.is_null(False))
            .join(MetaGroups, on=(InvTypes.metaGroupID == MetaGroups.metaGroupID))
            .where(MetaGroups.nameID == "Tech II")
        )

        result = [type.typeName for type in t2_search]

        return result

    @staticmethod
    @lru_cache(maxsize=2)
    def get_capital_ship() -> list:
        capital_ship_search = (
                InvTypes.select(InvTypes.typeName, InvTypes.typeID, InvTypes.marketGroupID)
                .join(InvGroups, on=(InvTypes.groupID == InvGroups.groupID))
                .join(InvCategories, on=(InvGroups.categoryID == InvCategories.categoryID))
                .where(InvCategories.categoryName == "Ship")
        )

        res = []
        for ship in capital_ship_search:
            market_list =SdeUtils.get_market_group_list(ship.typeID)
            if 'Capital Ships' in market_list:
                res.append(ship.typeName)

        res.remove('Venerable')
        res.remove('Vanguard')
        return res

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_groupname_by_id(invtpye_id: int) -> str:
        try:
            return (
                InvTypes.select(InvGroups.groupName)
                .join(InvGroups, on=(InvTypes.groupID == InvGroups.groupID))
                .switch(InvTypes)
                .where(InvTypes.typeID == invtpye_id).scalar()
            )
        except InvTypes.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_groupid_by_groupname(group_name: str) -> str:
        if (data := InvGroups.get_or_none(InvGroups.groupName == group_name)) is None:
            return None
        return data.groupID

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_invtpye_node_by_id(invtpye_id: int) -> InvTypes:
        try:
            return InvTypes.get(InvTypes.typeID == invtpye_id)
        except InvTypes.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_invtype_packagedvolume_by_id(invtpye_id: int) -> float:
        try:
            return InvTypes.get(InvTypes.typeID == invtpye_id).packagedVolume
        except InvTypes.DoesNotExist:
            return 0

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_metaname_by_metaid(meta_id: int) -> str:
        try:
            return MetaGroups.get(MetaGroups.metaGroupID == meta_id).nameID
        except MetaGroups.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_metaname_by_typeid(typeid: int) -> int:
        try:
            return (InvTypes.select(MetaGroups.nameID)
                       .join(MetaGroups, on=(InvTypes.metaGroupID == MetaGroups.metaGroupID))
                       .switch(InvTypes)
                       .where(InvTypes.typeID == typeid)
                       .scalar()
            )
        except DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_metadid_by_metaname(meta_name: int) -> int:
        try:
            return MetaGroups.get(MetaGroups.nameID == meta_name).metaGroupID
        except MetaGroups.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_id_by_name(name) -> int:
        try:
            if SdeUtils.maybe_chinese(name):
                return InvTypes_zh.get(InvTypes_zh.typeName == name).typeID
            return InvTypes.get(InvTypes.typeName == name).typeID
        except DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_name_by_id(type_id) -> str:
        try:
            return InvTypes.get(InvTypes.typeID == type_id).typeName
        except DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_id_by_cn_name(name) -> int:
        try:
            return InvTypes_zh.get(InvTypes_zh.typeName == name).typeID
        except InvTypes_zh.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_cn_name_by_id(type_id) -> str:
        try:
            return InvTypes_zh.get(InvTypes_zh.typeID == type_id).typeName
        except InvTypes_zh.DoesNotExist:
            return None

    @classmethod
    def get_market_group_tree(cls):
        if not cls._market_tree:
            g = nx.DiGraph()

            market_group_data = MarketGroups.select()
            for market_group in market_group_data:
                g.add_node(market_group.marketGroupID)
                if market_group.parentGroupID:
                    g.add_node(market_group.parentGroupID)
                    g.add_edge(market_group.parentGroupID, market_group.marketGroupID)
            cls._market_tree = g
        return cls._market_tree

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_market_group_name_by_groupid(market_group_id):
        name = MarketGroups.get(MarketGroups.marketGroupID == market_group_id).nameID

        return name

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_market_groupid_by_name(market_group_name: str) -> int:
        name = MarketGroups.select(MarketGroups.marketGroupID).where(MarketGroups.nameID == market_group_name).scalar()

        return name

    @classmethod
    @lru_cache(maxsize=1000)
    def get_market_group_list(cls, type_id: int) -> list[str]:
        market_tree = cls.get_market_group_tree()
        market_group_id = cls.get_invtpye_node_by_id(type_id).marketGroupID
        if market_group_id:
            market_group_list = [cls.get_name_by_id(type_id), cls.get_market_group_name_by_groupid(market_group_id)]
            parent_nodes = [parent_id for parent_id in market_tree.predecessors(market_group_id)]
            while parent_nodes:
                parent_node = parent_nodes[0]
                parent_name = cls.get_market_group_name_by_groupid(parent_node)
                market_group_list.append(parent_name)
                parent_nodes = [parent_id for parent_id in market_tree.predecessors(parent_node)]
            market_group_list.reverse()
            return market_group_list
        return []

        # market_group_id = cls.get_invtpye_node_by_id(type_id).marketGroupID
        # market_group_list = [cls.get_name_by_id(type_id), cls.get_market_group_name(market_group_id)]
        # while True:
        #     parent_id = MarketGroups.get_or_none(MarketGroups.marketGroupID == market_group_id)
        #     parent_id = parent_id.parentGroupID
        #     if not parent_id:
        #         market_group_list.reverse()
        #         return market_group_list
        #     parent_name = cls.get_market_group_name(parent_id)
        #     market_group_list.append(parent_name)
        #     market_group_id = parent_id


    @staticmethod
    @lru_cache(maxsize=1000)
    def get_category_by_id(type_id: int) -> str:
        try:
            return (
                InvTypes.select(InvCategories.categoryName)
                .join(InvGroups, on=(InvTypes.groupID == InvGroups.groupID))
                .join(InvCategories, on=(InvGroups.categoryID == InvCategories.categoryID))
                .where(InvTypes.typeID == type_id)
                .scalar()
            )
        except InvTypes.DoesNotExist:
            return None

    # @classmethod
    # def get_structure_info(cls, ac_token: str, structure_id: int) -> dict:
    #     """
    #     'name' = {str} '4-HWWF - WinterCo. Central Station'
    #     'owner_id' = {int} 98599770
    #     'position' = {dict: 3} {'x': -439918627801.0, 'y': -86578525155.0, 'z': -1177327092030.0}
    #     'solar_system_id' = {int} 30000240
    #     'type_id' = {int} 35834
    #     """
    #     info = universe_stations_station(structure_id) if len(str(structure_id)) <= 8 else universe_structures_structure(ac_token, structure_id)
    #     info.update({
    #         'system': MapSolarSystems.get(MapSolarSystems.solarSystemID==info[('system_id') if len(str(structure_id)) <= 8 else 'solar_system_id'])
    #                                  .solarSystemName,
    #         'structure_id': structure_id
    #     })
    #     return info

    @staticmethod
    def maybe_chinese(strs):
        en_count = 0
        cn_count = 0
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fa5':
                cn_count += 1
            elif 'a' <= _char <= 'z':
                en_count += 1
        return cn_count > en_count

    @lru_cache(maxsize=200)
    @staticmethod
    def fuzz_en_type(item_name, list_len) -> list[str]:
        choice = en_invtype_name_list
        result = process.extract(item_name, choice, scorer=fuzz.token_sort_ratio, limit=list_len)
        return [res[0] for res in result]

    @lru_cache(maxsize=200)
    @staticmethod
    def fuzz_zh_type(item_name, list_len) -> list[str]:
        choice = zh_invtype_name_list
        result = process.extract(item_name, choice, scorer=fuzz.token_sort_ratio, limit=list_len)
        return [res[0] for res in result]

    @staticmethod
    def fuzz_type(item_name, list_len = 5) -> list[str]:
        if SdeUtils.maybe_chinese(item_name):
            return SdeUtils.fuzz_zh_type(item_name, list_len)
        else:
            return SdeUtils.fuzz_en_type(item_name, list_len)

    type_stucture_cache = TTLCache(maxsize=1000, ttl=60 * 60 * 24)
    @staticmethod
    def get_structure_id_from_location_id(location_id, location_flag = None):
        if location_id in SdeUtils.type_stucture_cache:
            return SdeUtils.type_stucture_cache[location_id]
        else:
            structure_id, structure_flag = SdeUtils.find_type_structure(location_id, location_flag)
            SdeUtils.type_stucture_cache[location_id] = (structure_id, structure_flag)
            return structure_id, structure_flag

    @staticmethod
    def find_type_structure(location_id, location_flag = None):
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
            return SdeUtils.get_structure_id_from_location_id(father_data.location_id, father_data.location_type)
        return location_id, location_flag

    adjusted_price_cache = TTLCache(maxsize=1000, ttl=20 * 60)
    @cached(adjusted_price_cache)
    @staticmethod
    def get_adjusted_price_of_typeid(type_id: int):
        adjusted_price = MarketPriceCache.select(MarketPriceCache.adjusted_price).where(MarketPriceCache.type_id == type_id).scalar()

        if not adjusted_price:
            return 0
        return adjusted_price

    system_cos_cache = TTLCache(maxsize=1000, ttl=20 * 60)
    @cached(system_cos_cache)
    @staticmethod
    def get_system_cost(solar_system_id: int):
        res = SystemCostCache.get_or_none(SystemCostCache.solar_system_id == solar_system_id)

        if res:
            return res.manufacturing, res.reaction
        else:
            return 0.14, 0.14

    @staticmethod
    def get_all_type_id_in_market():
        result = InvTypes.select(InvTypes.typeID).where(InvTypes.marketGroupID.is_null(False))

        return [res.typeID for res in result]
