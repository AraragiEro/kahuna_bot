import json
import os
import asyncio
from urllib.parse import uses_query

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter import HandlerFilter
from astrbot.core.star.filter.custom_filter import CustomFilter
from astrbot.core.star.filter.permission import PermissionType
from astrbot.api import logger, llm_tool

from .src.event.utils import kahuna_debug_info
from .src.event.character import CharacterEvent
from .src.event.price import TypesPriceEvent
from .src.event.user import UserEvent
from .src.event.industry import AssetEvent, MarketEvent, IndsEvent, SdeEvent
from .src.event import llm_tool as kahuna_llmt
from .filter import AdminFilter, VipMemberFilter, MemberFilter

from .src.service.character_server.character_manager import CharacterManager
from .src.service.user_server.user_manager import UserManager
from .src.service.asset_server.asset_manager import AssetManager
from .src.service.market_server.market_manager import MarketManager
from .src.service.industry_server.structure import StructureManager
from .src.service.industry_server.industry_manager import IndustryManager
from .src.service.industry_server.industry_config import IndustryConfigManager

from .src.utils import refresh_per_min, run_func_delay_min

# 环境变量
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@register("KAHUNA_BOT", "Alero", "一个eveonline综合性插件", "0.0.1", "repo url")
class KahunaBot(Star):
    """
    The `MyPlugin` class.

    This is a plugin class for an EVE Online integrated application. It registers various command groups
    and commands to handle user interactions involving EVE Online in-game features such as market
    operations, character management, industry configurations, and more. This class leverages
    asynchronous tasks to initiate various periodic refresh jobs related to market, asset management,
    and industrial system data.

    Attributes
    ----------
    context : Context
        An instance of the `Context` class, used to provide the operational context for the plugin.
    """
    def __init__(self, context: Context):
        super().__init__(context)
        # 初始化
        # asyncio.create_task(self.init_plugin())

        # 延时初始化
        asyncio.create_task(run_func_delay_min(0, CharacterManager.refresh_all_characters_at_init))

        # 定时刷新任务
        asyncio.create_task(refresh_per_min(0, 360, MarketManager.refresh_market))
        asyncio.create_task(refresh_per_min(0, 10, AssetManager.refresh_all_asset))
        asyncio.create_task(refresh_per_min(0, 10, IndustryManager.refresh_running_status))
        asyncio.create_task(refresh_per_min(0, 60, IndustryManager.refresh_system_cost))
        asyncio.create_task(refresh_per_min(0, 60, IndustryManager.refresh_market_price))

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    # @filter.custom_filter(SelfFilter1)
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 获取消息的纯文本内容
        yield event.plain_result(f"Hello, {user_name}!") # 发送一条纯文本消息

    @filter.custom_filter(MemberFilter)
    @filter.command_group('角色', alias={"character"})
    async def character(self, event: AstrMessageEvent):
        pass

    @character.command('认证', alias={"auth"})
    async def character_auth(self, event: AstrMessageEvent):
        ''' 这是一个获取eve esi认证链接的指令 '''
        yield CharacterEvent.auth(event)

    @character.command('添加', alias={"add"})
    async def character_add(self, event: AstrMessageEvent, back_url: str):
        ''' 这是一个添加角色认证的指令，参数为认证完成后浏览器内的链接 '''
        yield CharacterEvent.add(event, back_url)

    @character.command('子角色', alias= {"addalias"})
    async def user_addalias(self, event: AstrMessageEvent, character_id_list: str):
        yield UserEvent.addalias(event)

    @filter.command("ojita")
    async def ojita(self, event: AstrMessageEvent, require_str: str):
        ''' 这是一个查询jita市场价格的插件 '''
        yield TypesPriceEvent.ojita_func(event, require_str)

    @filter.command("ofrt")
    async def ofrt(self, event: AstrMessageEvent, require_str: str):
        ''' 这是一个查询jita市场价格的插件 '''
        yield TypesPriceEvent.ofrt_func(event, require_str)

    @filter.custom_filter(AdminFilter)
    @filter.command_group("user")
    async def user(self, event: AstrMessageEvent):
        pass

    @user.command("create")
    async def user_create(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.add(event, user_qq)

    @user.command("addvip")
    async def user_addvip(self, event: AstrMessageEvent, user_qq: int, time_day: int):
        yield UserEvent.addMemberTime(event, user_qq, time_day)

    @user.command("del")
    async def user_del(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.deleteUser(event, user_qq)

    @user.command("clearvip")
    async def user_clearvip(self, event: AstrMessageEvent, user_qq: int):
        yield UserEvent.clearMemberTime(event, user_qq)

    @filter.command_group("我的", alias={"my"})
    async def my(self, event: AstrMessageEvent):
        pass

    @my.custom_filter(MemberFilter)
    @my.command('信息', alias={"info"})
    async def my_info(self, event: AstrMessageEvent):
        yield UserEvent.self_info(event)

    @my.custom_filter(MemberFilter)
    @my.command('主角色', alias={"setmain"})
    async def my_setmain(self, event: AstrMessageEvent):
        yield UserEvent.setMainCharacter(event)

    @filter.command('注册', alias={"sign"})
    async def my_sign(self, event: AstrMessageEvent):
        yield UserEvent.sign(event)

    @my.command("sheet")
    async def my_sheet(self, event: AstrMessageEvent, plan_name: str):
        """ 创建数据报表 """
        yield UserEvent.sheet_url(event, plan_name)

    @my.command("createsheet")
    async def my_createsheet(self, event: AstrMessageEvent):
        yield UserEvent.sheet_create(event)

    @filter.custom_filter(VipMemberFilter)
    @filter.command_group('资产', alias={"asset"})
    async def asset(self, event: AstrMessageEvent):
        pass

    @asset.custom_filter(AdminFilter)
    @asset.command("refall")
    async def asset_refall(self, event: AstrMessageEvent):
        yield AssetEvent.refall(event)

    @asset.group("owner")
    async def asset_owner(self, event: AstrMessageEvent):
        pass

    @asset_owner.command("add")
    async def asset_owner_add(self, event: AstrMessageEvent, owner_type: str, character_name: str):
        yield AssetEvent.owner_add(event, owner_type, character_name)

    @asset_owner.command("ref")
    async def asset_owner_ref(self, event: AstrMessageEvent, owner_type: str, character_name: str):
        yield AssetEvent.owner_refresh(event, owner_type, character_name)

    @asset.group('库存', alias={"container"})
    async def asset_container(self, event: AstrMessageEvent):
        pass

    @asset_container.command('添加', alias={"add"})
    async def asset_container_add(self, event: AstrMessageEvent, location_id: int, location_flag: str, target_qq: int, container_name: str):
        yield AssetEvent.container_add(event, location_id, location_flag, target_qq, container_name)

    @asset_container.command('列表', alias= {"ls"})
    async def asset_container_ls(self, event: AstrMessageEvent):
        yield AssetEvent.container_ls(event)

    @asset_container.command('查找', alias={"find"})
    async def asset_container_find(self, event: AstrMessageEvent, secret_type: str):
        yield AssetEvent.container_find(event, secret_type)

    @asset_container.command('设置标签', alias={"settag"})
    async def asset_container_settag(self, event: AstrMessageEvent, location_id_list: str, tag: str):
        yield AssetEvent.container_settag(event, location_id_list, tag)

    @filter.command_group("market")
    async def market(self, event: AstrMessageEvent):
        pass

    @filter.custom_filter(AdminFilter)
    @market.command("reforder")
    async def market_reforder(self, event: AstrMessageEvent):
        kahuna_debug_info(event)
        yield await MarketEvent.market_reforder(event)

    @filter.custom_filter(VipMemberFilter)
    @filter.command_group("工业", alias={'Inds'})
    async def Inds(self, event: AstrMessageEvent):
        """ 工业类指令组 """
        pass

    @Inds.group("匹配器", alias={'matcher'})
    async def Inds_matcher(self, event: AstrMessageEvent):
        """ 自定义工业系数适配器 """
        pass

    @Inds_matcher.command('创建', alias={"create"})
    async def Inds_matcher_create(self, event: AstrMessageEvent, matcher_name: str, matcher_type:str):
        yield IndsEvent.matcher_create(event, matcher_name, matcher_type)

    @Inds_matcher.command('删除', alias={"del"})
    async def Inds_matcher_del(self, event: AstrMessageEvent, matcher_name: str):
        yield IndsEvent.matcher_del(event, matcher_name)

    @Inds_matcher.command('列表', alias={"ls"})
    async def Inds_matcher_ls(self, event: AstrMessageEvent):
        """ 获取当前用户所有匹配器 """
        yield IndsEvent.matcher_ls(event)

    @Inds_matcher.command('详情', alias={"info"})
    async def Inds_matcher_info(self, event: AstrMessageEvent, matcher_name: str):
        """ 获取匹配器详情 """
        yield IndsEvent.matcher_info(event, matcher_name)

    @Inds_matcher.command('设置', alias={"set"})
    async def Inds_matcher_set(self, event: AstrMessageEvent, matcher_name: str, matcher_key_type: str):
        """ 配置匹配器 set {matcher_name[bp_matcher]} {matcher_key_type} {mater_eff} {time_eff}"""
        """ 配置匹配器 set {matcher_name[st_matcher]} {matcher_key_type} {mater_eff} {bp_name} {structure_id} """
        yield IndsEvent.matcher_set(event, matcher_name, matcher_key_type)

    @Inds_matcher.command('取消', alias= {"unset"})
    async def Inds_matcher_unset(self, event: AstrMessageEvent, matcher_name: str, matcher_key_type: str):
        """ 配置匹配器 set {matcher_name} {matcher_key_type} {mater_eff} {time_eff}"""
        yield IndsEvent.matcher_unset(event, matcher_name, matcher_key_type)

    @Inds.group('建筑', alias={"structure"})
    async def Inds_structure(self, event: AstrMessageEvent):
        pass

    @Inds_structure.command('列表', alias={"ls"})
    async def Inds_structure_ls(self, event: AstrMessageEvent):
        ''' 打印已保存的建筑信息 '''
        yield IndsEvent.structure_ls(event)

    @Inds_structure.command('信息', alias={"info"})
    async def Inds_structure_info(self, event: AstrMessageEvent, structure_id: int):
        ''' 打印指定id的建筑信息 '''
        yield IndsEvent.structure_info(event, structure_id)

    @Inds_structure.command('设置', alias={"set"})
    async def Inds_structure_set(self, event: AstrMessageEvent, structure_id: int, mater_rig_level: int, time_rig_level: int):
        yield IndsEvent.structure_set(event, structure_id, mater_rig_level, time_rig_level)

    @Inds.group('计划', alias={"plan"})
    async def Inds_plan(self, event: AstrMessageEvent):
        pass

    @Inds_plan.command('创建计划', "create")
    async def Inds_plan_create(self, event: AstrMessageEvent, plan_name: str,
                               bp_matcher: str, st_matcher: str, prod_block_matcher: str
                               ):
        yield IndsEvent.plan_create(event, plan_name, bp_matcher, st_matcher, prod_block_matcher)

    @Inds_plan.command('设置时间', alias={"setcycletime"})
    async def Inds_plan_setcycletime(self, event: AstrMessageEvent, plan_name: str, tpye: str, cycle_time: int):
        yield IndsEvent.plan_setcycletime(event, plan_name, tpye, cycle_time)

    # @Inds_plan.command({"setline"})
    # async def Inds_plan_setline(self, event: AstrMessageEvent, plan_name: str, tpye: str, line: int):
    #     yield IndsEvent.plan_set_line(event, plan_name, tpye, line)

    @Inds_plan.command('列表', alias= {"ls"})
    async def Inds_plan_ls(self, event: AstrMessageEvent, plan_name: str):
        yield IndsEvent.plan_ls(event, plan_name)

    @Inds_plan.command('增加产品', alias={"setprod"})
    async def Inds_plan_setprod(self, event: AstrMessageEvent, plan_name: str):
        yield IndsEvent.plan_setprod(event, plan_name)

    @Inds_plan.command('删除产品', alias={"delprod"})
    async def Inds_plan_delprod(self, event: AstrMessageEvent, plan_name: str, index: str):
        yield IndsEvent.plan_delprod(event, plan_name, index)

    @Inds_plan.command('删除计划', alias={"delplan"})
    async def Inds_plan_delplan(self, event: AstrMessageEvent, plan_name: str):
        yield IndsEvent.plan_delplan(event, plan_name)

    @Inds_plan.command('顺序交换', alias={"changeindex"})
    async def Inds_plan_changeindex(self, event: AstrMessageEvent, plan_name: str, index: int, new_index: int):
        yield IndsEvent.plan_changeindex(event, plan_name, index, new_index)

    @Inds_plan.command('屏蔽库存', alias={"hidecontainer"})
    async def Inds_plan_hidecontainer(self, event: AstrMessageEvent, plan_name: str, container_id: int):
        yield IndsEvent.plan_hidecontainer(event, plan_name, container_id)

    @Inds_plan.command('取消屏蔽库存', alias={"unhidecontainer"})
    async def Inds_plan_unhidecontainer(self, event: AstrMessageEvent, plan_name: str, container_id: int):
        yield IndsEvent.plan_unhidecontainer(event, plan_name, container_id)

    @Inds.group('报表', alias={"rp"})
    async def Inds_rp(self, event: AstrMessageEvent):
        pass

    @Inds_rp.command('计划报表', alias={'workrp'})
    async def Inds_rp_workrp(self, event: AstrMessageEvent, plan_name: str):
        """ 计划材料清单 """
        yield await IndsEvent.rp_all(event, plan_name)

    @Inds_rp.command('t2市场', alias={'t2mk'})
    async def Inds_rp_t2cost(self, event: AstrMessageEvent, plan_name: str):
        yield await IndsEvent.rp_t2mk(event, plan_name)

    @Inds_rp.command('旗舰成本', alias={'capcost'})
    async def Inds_rp_capcost(self, event: AstrMessageEvent, plan_name: str):
        yield await IndsEvent.rp_capcost(event, plan_name)

    @Inds_rp.command('单品成本', alias={'costdetail'})
    async def Inds_rp_costdetail(self, event: AstrMessageEvent, plan_name: str, product_name: str):
        yield await IndsEvent.rp_costdetail(event, plan_name, product_name)

    @Inds.command("refjobs")
    async def Inds_refjobs(self, event: AstrMessageEvent):
        """ 刷新进行中的工作 """
        yield IndsEvent.refjobs(event)

    @Inds.command('指南', alias={'help'})
    async def Inds_help(self, event: AstrMessageEvent):
        yield event.plain_result(f"KAHUNA工业核心初级指南: https://conscious-cord-0d1.notion.site/bot-1920b0a9ac1b80998d71c4349b241145?pvs=4")

    @filter.custom_filter(VipMemberFilter)
    @filter.command_group("sde")
    async def sde(self, event: AstrMessageEvent):
        """ 查询sde数据库信息相关指令 """
        pass

    @sde.command("type")
    async def sde_type(self, event: AstrMessageEvent, message: str):
        yield SdeEvent.type(event)

    @sde.command("find")
    async def sde_findtype(self, event: AstrMessageEvent, message: str):
        yield SdeEvent.findtype(event)

    @sde.command("id")
    async def sde_id(self, event: AstrMessageEvent, tid: int):
        yield SdeEvent.type_id(event, tid)

    # @filter.command("test")
    # async def test(self, event: AstrMessageEvent, require_str: str):
    #     yield TypesPriceEvent.test_func(event, require_str)

    """ 自然语言指令集 """
    @llm_tool(name='eve_knowlage_bot')
    async def eve_knowlage_bot(self, event: AstrMessageEvent, question_str: str) -> MessageEventResult:
        ''' 向eveonline和FRT兄弟会wiki知识库机器人提问获得eveonline或FRT联盟wiki相关内容。

        Args:
            question_str(string): 用于向evewiki聊天机器人提问的文本。
        '''
        yield await kahuna_llmt.return_evebot_result(self, event, question_str)

    @llm_tool(name="get_eve_industry_report")  # 如果 name 不填，将使用函数名
    async def get_eve_industry_report(self, event: AstrMessageEvent, plan_name: str) -> MessageEventResult:
        ''' 获取eveonline游戏的工业计划报表。

        Args:
            plan_name(string): 计划名称
        '''
        tool_result = await IndsEvent.rp_all(event, plan_name)
        yield await kahuna_llmt.return_tool_result_with_llm(self, event, tool_result)

    @llm_tool(name="get_eve_capital_cost_with_plan_data")  # 如果 name 不填，将使用函数名
    async def get_eve_capital_cost_with_plan_data(self, event: AstrMessageEvent, plan_name: str) -> MessageEventResult:
        ''' 根据给定的计划中的数据计算eveonline游戏中旗舰种类舰船的成本。

        Args:
            plan_name(string): 计划名称
        '''
        tool_result = await IndsEvent.rp_capcost(event, plan_name)
        yield await kahuna_llmt.return_tool_result_with_llm(self, event, tool_result)

    @llm_tool(name="get_eve_t2_cost_with_plan_data")  # 如果 name 不填，将使用函数名
    async def get_eve_t2_cost_with_plan_data(self, event: AstrMessageEvent, plan_name: str) -> MessageEventResult:
        ''' 根据给定的计划中的数据计算eveonline游戏中T2科技等级种类舰船的成本、利润、流水等市场信息。

        Args:
            plan_name(string): 计划名称
        '''
        tool_result = await IndsEvent.rp_t2mk(event, plan_name)
        yield await kahuna_llmt.return_tool_result_with_llm(self, event, tool_result)
