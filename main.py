import json
import os

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter.permission import BasePermissionTypeFilter
from astrbot.core.star.filter import HandlerFilter
from astrbot.api import logger

from .src.event.utils import kahuna_debug_info
from .src.event.character import CharacterEvent
from .src.event.price import TypesPriceEvent
from .src.event.user import UserEvent
from .src.event.industry import AssetEvent, MarketEvent

# 环境变量
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

qq_list = [461630479]

class SelfFilter(BasePermissionTypeFilter):
    def __init__(self, raise_error: bool = True):
        self.raise_error = raise_error

    def filter(self, event: AstrMessageEvent ,cfg) -> bool:
        '''过滤器
        '''
        if int(event.get_sender_id()) in qq_list:
            logger.info(f"event.get_sender_id(): {event.get_sender_id()} True")
            return True
        logger.info(f"event.get_sender_id(): {event.get_sender_id()} False")
        return False


@register("KAHUNA_BOT", "Alero", "一个eveonline综合性插件", "0.0.1", "repo url")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.custom_permission_type(SelfFilter)
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 获取消息的纯文本内容
        yield event.plain_result(f"Hello, {user_name}!") # 发送一条纯文本消息

    @filter.command_group("character")
    async def character(self, event: AstrMessageEvent):
        pass

    @character.command("auth")
    async def character_auth(self, event: AstrMessageEvent):
        ''' 这是一个获取eve esi认证链接的指令 '''
        yield CharacterEvent.auth(event)

    @character.command("add")
    async def character_add(self, event: AstrMessageEvent, back_url: str):
        ''' 这是一个添加角色认证的指令，参数为认证完成后浏览器内的链接 '''
        yield CharacterEvent.add(event, back_url)

    @filter.command("ojita")
    async def ojita(self, event: AstrMessageEvent, require_str: str):
        ''' 这是一个查询jita市场价格的插件 '''
        print(event.message_str)
        yield TypesPriceEvent.ojita_func(event, " ".join(event.message_str.split(" ")[1:]))

    @filter.command("ofrt")
    async def ofrt(self, event: AstrMessageEvent, require_str: str):
        ''' 这是一个查询jita市场价格的插件 '''
        yield TypesPriceEvent.ofrt_func(event, " ".join(event.message_str.split(" ")[1:]))

    @filter.command_group("user")
    async def user(self, event: AstrMessageEvent):
        pass

    @user.command("create")
    async def user_create(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.add(event, user_qq)

    @user.command("addvip")
    async def user_addvip(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.addMemberTime(event, user_qq)

    @user.command("del")
    async def user_del(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.deleteUser(event, user_qq)

    @user.command("clearvip")
    async def user_clearvip(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.clearMemberTime(event, user_qq)

    @filter.command_group("my")
    async def my(self, event: AstrMessageEvent):
        pass

    @my.command("info")
    async def my_info(self, event: AstrMessageEvent):
        yield UserEvent.self_info(event)

    @my.command("setmain")
    async def my_setmain(self, event: AstrMessageEvent):
        yield UserEvent.setMainCharacter(event)

    @my.command("sign")
    async def my_sign(self, event: AstrMessageEvent):
        yield UserEvent.sign(event)

    @filter.command_group("asset")
    async def asset(self, event: AstrMessageEvent):
        pass

    @asset.group("owner")
    async def asset_owner(self, event: AstrMessageEvent):
        pass

    @asset_owner.command("add")
    async def asset_owner_add(self, event: AstrMessageEvent, owner_type: str, character_name: str):
        yield AssetEvent.owner_add(event, owner_type, character_name)

    @asset_owner.command("refresh")
    async def asset_owner_refresh(self, event: AstrMessageEvent, owner_type: str, character_name: str):
        yield AssetEvent.owner_refresh(event, owner_type, character_name)

    @asset.group("container")
    async def asset_container(self, event: AstrMessageEvent):
        pass

    @asset_container.command("add")
    async def asset_container_add(self, event: AstrMessageEvent, location_id: int, location_flag: str, target_qq: int, container_name: str):
        yield AssetEvent.container_add(event, location_id, location_flag, target_qq, container_name)

    @asset_container.command("ls")
    async def asset_container_ls(self, event: AstrMessageEvent):
        yield AssetEvent.container_ls(event)

    @asset_container.command("find")
    async def asset_container_find(self, event: AstrMessageEvent, secret_type: int):
        yield AssetEvent.container_find(event, secret_type)

    @asset_container.command("settag")
    async def asset_container_settag(self, event: AstrMessageEvent, location_id_list: str, tag: str):
        yield AssetEvent.container_settag(event, location_id_list, tag)

    @filter.command_group("market")
    async def market(self, event: AstrMessageEvent):
        pass

    @market.command("reforder")
    async def market_reforder(self, event: AstrMessageEvent):
        kahuna_debug_info(event)
        yield MarketEvent.market_reforder(event)