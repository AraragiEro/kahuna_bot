
def main():
    import os, sys
    os.environ['KAHUNA_BOT_TEST'] = '1'
    os.environ["KAHUNA_DB_DIR"] = "F:/WorkSpace/GIT/kahuna_bot/kahuna_bot/"

    from kahuna.service.asset_server import AssetContainer, AssetManager
    from kahuna.service.evesso_server.eveesi import characters_character, characters_character_id_industry_jobs
    from kahuna.service.character_server import CharacterManager
    from kahuna.service.evesso_server.eveesi import verify_token, industry_systems
    from kahuna.service.market_server import MarketManager
    from kahuna.service.industry_server.running_job import RunningJobOwner
    from kahuna.service.industry_server.industry_manager import IndustryManager
    from kahuna.service.industry_server.system_cost import SystemCost

    # MarketManager.refresh_market()

    # character_verify_data = characters_character(2115643725)
    # res = AssetManager.add_container(461630479, 1035585843514, 'CorpSAG2', 'Alero-4H公司2号机库', 461630479)
    # a, b = AssetContainer.find_type_structure(res[0].location_id)

    # res = AssetContainer.find_container("Tungsten", 461630479)
    # AssetManager.refresh_all_asset()
    AA = CharacterManager.get_character_by_name_qq("AServant", 461630479)
    KK = CharacterManager.get_character_by_name_qq("Kahuna Poi", 523585918)
    # res = characters_character_id_industry_jobs(AA.ac_token, AA.character_id)
    # res = CharacterManager.is_character_corp_directer(KK)
    # IndustryManager.refresh_running_status()
    # res = industry_systems()
    res = SystemCost.refresh_system_cost()

    print(111)

if __name__ == '__main__':
    main()