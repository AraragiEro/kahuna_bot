
from ..character_server import CharacterManager
from ..database_server.model import BlueprintAssetCache
from ..asset_server.asset_container import AssetContainer
from .blueprint import BPManager
from ..sde_service import SdeUtils

NULL_MANU_SEC_BONUS = 2.1
NULL_REAC_SEC_BONUS = 1.1

T1_MANU_MATER_EFF = 1 - 0.02 * NULL_MANU_SEC_BONUS
T1_MANU_TIME_EFF = 1 - 0.2 * NULL_MANU_SEC_BONUS

T2_MANU_MATER_EFF = 1 - 0.024 * NULL_MANU_SEC_BONUS
T2_MANU_TIME_EFF = 1 - 0.24 * NULL_MANU_SEC_BONUS

T1_REAC_MATER_EFF = 1 - 0.02 * NULL_REAC_SEC_BONUS
T1_REAC_TIME_EFF = 1 - 0.2 * NULL_REAC_SEC_BONUS

T2_REAC_MATER_EFF = 1 - 0.024 * NULL_REAC_SEC_BONUS
T2_REAC_TIME_EFF = 1 - 0.24 * NULL_REAC_SEC_BONUS

MANU_STRUCTURE_MATER_EFF = 1 - 0.01

SMALL_STRUCTURE_MANU_TIME_EFF = 1 - 0.15
MID_STRUCTURE_MANU_TIME_EFF = 1 - 0.2
LARGE_STRUCTURE_MANU_TIME_EFF = 1 - 0.3

MID_STRUCTURE_REAC_TIME_EFF = 1 - 0.25
SMALL_STRUCTURE_REAC_TIME_EFF = 0

SKILL_TIME_EFF = 1 - 0.392

class IndustryConfig:
    config_owner = "default"

    # 最终材料效率为：
    #   蓝图效率 * 建筑效率
    # 蓝图效率获取优先级：
    #   特别设置的蓝图效率 > 蓝图资产效率 > 默认蓝图效率
    # 建筑效率获取优先级
    #   特别设置的建筑效率 > 蓝图资产所在建筑效率 > 默认建筑效率

    # 默认蓝图材料效率
    default_faction_material_efficiency = 0
    default_t2_material_efficiency = 0.02
    default_other_material_efficiency = 0.1

    # 默认蓝图时间效率
    default_faction_time_efficiency = 0
    default_t2_time_efficiency = 0.04
    default_other_time_efficiency = 0.2


    default_reac_structure = 0
    default_manu_structure = 0
    default_manu_structure = 0

    @classmethod
    def get_eff(cls, source_id: int) -> tuple[int, int]:
        # TODO:　根据制品类型获取双系数
        mater_eff = 1
        time_eff = 1

        action_id = BPManager.get_action_id(source_id)
        group_name = SdeUtils.get_groupname_by_id(source_id)
        # category = SdeUtils.get_category_by_id(source_id)

        if action_id == 11:
            mater_eff = 1

        return mater_eff, time_eff

    @classmethod
    def get_runs_list_by_bpasset(cls, total_runs_needed: int, source_id: int, user_qq: int, location_id: int) -> list:
        # 根据库存蓝图生成工作序列
        # 使用优先级：
        # -1无限 > 从大到小匹配直到 剩余流程大于最大蓝图流程， 然后从小到大匹配知道剩余流程归0
        # 使用完现有蓝图后，如果还有剩余流程，根据类型使用默认蓝图流程，不匹配的使用无限流程

        # owner_qq可用的蓝图仓库，即container_tag为bp的仓库
        bp_container_list = AssetContainer.get_location_id_by_qq_tag(user_qq, "bp")

        # 根据source_id获得user_qq所属的所有蓝图
        owner_id_set = set(character.character_id for character in CharacterManager.get_user_all_characters(user_qq))
        for character in CharacterManager.get_user_all_characters(user_qq):
            if character.director:
                owner_id_set.add(character.corp_id)
        bp_id = BPManager.get_bp_id_by_product(source_id)
        avalable_bpc_asset = BlueprintAssetCache.select().where((BlueprintAssetCache.location_id << bp_container_list) &
                                                                (BlueprintAssetCache.type_id == bp_id) &
                                                                (BlueprintAssetCache.quantity < 0))
        avaliable_bpo_asset = BlueprintAssetCache.select().where((BlueprintAssetCache.location_id << bp_container_list) &
                                                                 (BlueprintAssetCache.type_id == bp_id) &
                                                                 (BlueprintAssetCache.quantity > 0))

        # 可用的拷贝序列 [(runs, material_efficiency, time_efficiency, item_id)]
        avaliable_bpc_list = [(bp.runs, bp.material_efficiency, bp.time_efficiency, bp.item_id) for bp in avalable_bpc_asset]
        avaliable_bpc_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
        # 可用的原图序列 [(quantity, material_efficiency, time_efficiency)]
        avaliable_bpo_count = dict()
        for bpo in avaliable_bpo_asset:
            if (bpo.material_efficiency, bpo.time_efficiency) not in avaliable_bpo_count:
                avaliable_bpo_count[(bpo.material_efficiency, bpo.time_efficiency)] = 0
            avaliable_bpo_count[(bpo.material_efficiency, bpo.time_efficiency)] += bpo.quantity
        avaliable_bpo_count_list = [(v, k[0], k[1]) for k, v in avaliable_bpo_count.items()]
        avaliable_bpo_count_list.sort(key=lambda x: x[1], reverse=True)


        # TODO: 获取建筑时间效率以计算最佳周期轮数

        # TODO 计算工作序列
        production_time = BPManager.get_production_time(source_id)
        for bpo in avaliable_bpo_count_list:
            pass



