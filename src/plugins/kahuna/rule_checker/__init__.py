from nonebot.adapters.onebot.v11.event import (PrivateMessageEvent,
                                               GroupMessageEvent)
from nonebot.rule import is_type
from nonebot.params import Event

class RuleChecker(object):
    is_private = is_type(PrivateMessageEvent)
    is_group = is_type(GroupMessageEvent)
