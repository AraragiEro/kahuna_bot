from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

def kahuna_debug_info(event: AstrMessageEvent):
    # debug info
    user_qq = event.message_obj.raw_message.user_id
    logger.info(f"init info complete\n"
                 f"  user_qq: {user_qq}\n"
                 f"  command: {event.message_str}\n")

    return user_qq