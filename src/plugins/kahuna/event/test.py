# nonebot model
from nonebot.params import Command
from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher
from nonebot import on_command

# permission checker
from ..permission_checker import PermissionChecker

# rule checker
from ..rule_checker import RuleChecker

# kahuna model
from .. import config

# import Exception

# import logger
from ..service.log_server import logger


test_event = on_command(
    ("ttt"),
    aliases={("ttt", "bbb"),
             ("ttt", "aaa")},
    rule=RuleChecker.is_private,
    permission=PermissionChecker.admin,
    priority=10, block=True)
@test_event.handle()
async def test_event_func(matcher: Matcher,
                            event: Event,
                            # args: Message = CommandArg(),
                            cmd: tuple[str, ...] = Command()):
    HELP = """
user.createUser [qq]
user.addMemberTime [qq] [day]
user.clearMemberTime [qq]
user.deleteUser [qq]
"""
    logger.debug(config.db_dir)


    # if len(cmd) == 1:
    await matcher.finish(config.db_dir)