import math

from .blueprint import BPManager
from ..sde_service import SdeUtils
from cachetools import cached, TTLCache
from ..user_server.user_manager import UserManager
from ..character_server.character_manager import CharacterManager
from .structure import StructureManager

from .blueprint import BPManager
from .industry_config import IndustryConfigManager

class IdsUtils:
    eiv_cache = TTLCache(maxsize=1024, ttl=3600)
    @cached(eiv_cache)
    @staticmethod
    def get_eiv(type_id) -> int:
        bp_materials = BPManager.get_bp_materials(type_id)
        production_quantity = BPManager.get_bp_product_quantity_typeid(type_id)
        eiv = 0
        for child_id, quantity in bp_materials.items():
            eiv += quantity * SdeUtils.get_adjusted_price_of_typeid(child_id)

        return eiv / production_quantity

    @classmethod
    def check_job_material_avaliable(cls, type_id, work, asset_dict):
        bp_materials = BPManager.get_bp_materials(type_id)
        for child_id, quantity in bp_materials.items():
            child_need = math.ceil(quantity * work.runs * work.mater_eff)
            if child_need > asset_dict.get(child_id, 0):
                return False

        for child_id, quantity in bp_materials.items():
            child_need = math.ceil(quantity * work.runs * work.mater_eff)
            asset_dict[child_id] -= child_need
        return True

    @classmethod
    def get_eiv_cost(cls, child_id, child_total_quantity: int, owner_qq: int, st_matcher):
        """ 获取系数成本 """
        character_id = UserManager.get_main_character_id(owner_qq)
        character = CharacterManager.get_character_by_id(character_id)
        structure_id = IndustryConfigManager.allocate_structure(child_id, st_matcher)
        structure = StructureManager.get_structure(structure_id, character.ac_token)
        eiv_cost_eff = IndustryConfigManager.get_structure_EIV_cost_eff(structure.type_id)
        sys_manu_cost, sys_reac_cost = SdeUtils.get_system_cost(structure.solar_system_id)
        child_eiv = cls.get_eiv(child_id) * child_total_quantity
        action_id = BPManager.get_action_id(child_id)

        if action_id == 1:
            child_eiv_cost = child_eiv * ((0.04 + 0.0001 + 0.0005) + (sys_manu_cost * (1 - eiv_cost_eff)))
        else:
            child_eiv_cost = child_eiv * ((0.04 + 0.0001 + 0.0005) + (sys_reac_cost * (1 - eiv_cost_eff)))

        return child_eiv_cost

    @classmethod
    def get_logistic_need_data(cls, owner_qq: int, child_id: int, st_matcher: str, quantity: int):
        character_id = UserManager.get_main_character_id(owner_qq)
        character = CharacterManager.get_character_by_id(character_id)
        structure_id = IndustryConfigManager.allocate_structure(child_id, st_matcher)
        structure = StructureManager.get_structure(structure_id, character.ac_token)

        return [child_id, structure, quantity]

