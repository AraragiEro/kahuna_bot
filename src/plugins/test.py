
# def test1():
#     import networkx as nx
#     from ..service.industry_server.blueprint import get_bp_materials
#     from ..service.industry_server.item import get_name_by_id, get_id_by_name
#     from ..service.industry_server.blueprint_analyse import BpAnalyser
#
#     bpa = BpAnalyser(cal_type="work")
#     material_dict = bpa.get_product_ori_materials("Ishtar", 1)
#
#     print(111)

# def test2():
#     from ..service.character_server.character_manager import CharacterManager
#
#     # CharacterManager.refresh_character_token(2115643725)
#     from ..service.evesso_server.oauth import get_token
#     from ..service.evesso_server.oauth import refresh_token
#     refresh_token("1231312313")
#     print(111)

# def main():
#     REGION_FORGE_ID = 10000002
#     JITA_TRADE_HUB_STRUCTURE_ID = 60003760
#     FRT_4H_STRUCTURE_ID = 1035466617946
#     from ..service.character_server.character_manager import CharacterManager
#     from ..service.evesso_server.eveesi import markets_region_orders, markets_structures
#     from ..service.database_server.model import MarketOrder
#     from ..service.market_server.market_manager import Market
#     from ..service.evesso_server.eveutils import find_max_page
#     frt_market = Market("frt")
#     frt_market.access_character = CharacterManager.character_dict[2115643725]
#     frt_market.get_jita_order()
#     # max_page = await find_max_page(markets_region_orders, REGION_FORGE_ID)
#     # res = markets_structures(1, frt_market.access_character.ac_token, FRT_4H_STRUCTURE_ID)
#     print(111)

def main():
    import os, sys
    os.environ['TEST'] = '1'
    os.environ["KAHUNA_DB_DIR"] = "D:\workspace\kahuna_bot\kahuna_bot"

    from kahuna.service.character_server import CharacterManager
    from kahuna.service.evesso_server.eveesi import universe_structures_structure,characters_character
    from kahuna.service.asset_server import AssetManager
    alero  = CharacterManager.character_dict[2115643725]
    # asset = Asset("character", 2115643725, alero)

    # asset.get_character_asset()
    # AssetManager.copy_to_cache()
    c_info = characters_character(alero.character_id)
    asset = AssetManager.create_asset(alero.QQ, "corp", int(c_info["corporation_id"]), alero)
    asset.asset_item_count
    print(111)

if __name__ == '__main__':
    main()