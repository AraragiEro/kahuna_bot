# import logger
from astrbot.api import logger

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register

# kahuna model
from .utils import kahuna_debug_info
from ..service.asset_server import AssetManager
from ..service.character_server import CharacterManager
from ..service.evesso_server.eveesi import characters_character
from ..service.market_server import MarketManager
from ..service.asset_server import AssetContainer


# import Exception
from ..utils import KahunaException

class AssetEvent():
    @staticmethod
    def get_owner_id(owner_type: str, character_name: str, character) -> int:
        if owner_type == "corp":
            character_info = characters_character(character.character_id)
            owner_id = int(character_info["corporation_id"])
        elif owner_type == "character":
            owner_id = character.character_id
        else:
            raise KahunaException("owner_type must be 'corp' or 'character'")

        return owner_id

    @staticmethod
    def owner_add(event: AstrMessageEvent, owner_type: str, character_name: str):
        user_qq = int(event.get_sender_id())
        character = CharacterManager.get_character_by_name_qq(character_name, user_qq)

        owner_id = AssetEvent.get_owner_id(owner_type, character_name, character)

        asset = AssetManager.create_asset(user_qq, owner_type, owner_id, character)
        return event.plain_result(f"库存已成功创建。\n"
                                  f"库存条目 {asset.asset_item_count}")

    @staticmethod
    def owner_refresh(event: AstrMessageEvent, owner_type: str, character_name: str):
        user_qq = int(event.get_sender_id())
        character = CharacterManager.get_character_by_name_qq(character_name, user_qq)

        owner_id = AssetEvent.get_owner_id(owner_type, character_name, character)

        asset = AssetManager.refresh_asset(owner_type, owner_id)
        return event.plain_result("刷新完成")

    @staticmethod
    def container_add(event: AstrMessageEvent, location_id: int, location_flag: str, target_qq: int, container_name: str):
        user_qq = event.get_sender_id()

        container = AssetManager.add_container(target_qq, location_id, location_flag, container_name, user_qq)
        print_info = (f"已授权 {target_qq} 使用属于 {user_qq} 的库存: {location_id}。\n")
        return event.plain_result(print_info)

    @staticmethod
    def container_ls(event: AstrMessageEvent):
        user_qq = int(event.get_sender_id())
        print_str = "你可访问以下库存：\n"
        for container in AssetManager.container_dict.values():
            if AssetContainer.operater_has_container_permission(user_qq, container.asset_owner_id):
                print_str += f"{container}\n"
        return event.plain_result(print_str)

    @staticmethod
    def container_find(event: AstrMessageEvent, secret_type: int):
        user_qq = event.get_sender_id()
        container_info = AssetContainer.find_container(secret_type, user_qq)

        print_info = f"找到{len(container_info)}个符合条件的库存空间。\n"
        for container in container_info:
            print_info += (f"\n建筑名：{container['name']} 数量：{container['exist_quantity']}\n"
                           f"建筑类型：{container['structure_type']}\n"
                           f"星系：{container['system']}\n"
                           f"添加库存指令：.asset container add {container['location_id']} {container['location_flag']} [授权目标qq] [库存空间别名]\n")
        return event.plain_result(print_info)

    @staticmethod
    def container_settag(event: AstrMessageEvent, location_id_list: str, tag: str):
        user_qq = event.get_sender_id()
        location_id_list = location_id_list.split(",")
        success_list = AssetManager.set_container_tag([(user_qq, location_id) for location_id in location_id_list], tag)

        print_str = "成功设置以下库存tag：\n"
        for container in success_list:
            print_str += f"{container.asset_location_id}: {container.tag}\n"

        return event.plain_result(print_str)

class MarketEvent():
    @staticmethod
    def market_reforder(event: AstrMessageEvent):
        res_log = MarketManager.refresh_market()
        return event.plain_result(res_log)