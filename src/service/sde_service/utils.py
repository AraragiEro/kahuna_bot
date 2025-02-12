from functools import lru_cache
from pydantic import BaseModel
import networkx as nx
from thefuzz import fuzz, process

from ...service.sde_service.database import InvTypes, InvGroups, InvCategories
from ...service.sde_service.database import MetaGroups, MarketGroups
from ..database_server.model import InvTypeMap

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
    def get_t2_ship() -> list:
        t2_search = (
            InvTypes.select(InvTypes.typeName)
            .join(InvGroups, on=(InvTypes.groupID == InvGroups.groupID))
            .join(InvCategories, on=(InvGroups.categoryID == InvCategories.categoryID))
            .where(InvCategories.categoryName == "Ship")
            .switch(InvTypes)
            .join(MetaGroups, on=(InvTypes.metaGroupID == MetaGroups.metaGroupID))
            .where(MetaGroups.nameID == "Tech II")
        )

        result = [type.typeName for type in t2_search]

        return result

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
    def get_invtpye_node_by_id(invtpye_id: int) -> InvTypes:
        try:
            return InvTypes.get(InvTypes.typeID == invtpye_id)
        except InvTypes.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=100)
    def get_meta(meta_id: int) -> str:
        try:
            return MetaGroups.get(MetaGroups.metaGroupID == meta_id).nameID
        except MetaGroups.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_id_by_name(name) -> int:
        try:
            return InvTypes.get(InvTypes.typeName == name).typeID
        except InvTypes.DoesNotExist:
            return None

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_name_by_id(type_id) -> str:
        try:
            return InvTypes.get(InvTypes.typeID == type_id).typeName
        except InvTypes.DoesNotExist:
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
        g = nx.DiGraph()

        market_group_data = MarketGroups.select()
        for market_group in market_group_data:
            g.add_node(market_group.marketGroupID)
            if market_group.parentGroupID:
                g.add_node(market_group.parentGroupID)
                g.add_edge(market_group.parentGroupID, market_group.marketGroupID)

        return g

    @classmethod
    @property
    def market_tree(cls):
        if not cls._market_tree:
            cls.market_tree = cls.get_market_group_tree()
        return cls._market_tree

    @staticmethod
    @lru_cache(maxsize=50)
    def get_market_group_name(market_group_id):
        name = MarketGroups.get(MarketGroups.marketGroupID == market_group_id).nameID

        return name

    @staticmethod
    def get_category_by_id():
        pass

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
    def fuzz_en_type(item_name) -> list[str]:
        choice = en_invtype_name_list
        result = process.extract(item_name, choice, scorer=fuzz.token_sort_ratio, limit=5)
        return [res[0] for res in result]

    @lru_cache(maxsize=200)
    @staticmethod
    def fuzz_zh_type(item_name) -> list[str]:
        choice = zh_invtype_name_list
        result = process.extract(item_name, choice, scorer=fuzz.token_sort_ratio, limit=5)
        return [res[0] for res in result]

    @staticmethod
    def fuzz_type(item_name) -> list[str]:
        if SdeUtils.maybe_chinese(item_name):
            return SdeUtils.fuzz_zh_type(item_name)
        else:
            return SdeUtils.fuzz_en_type(item_name)