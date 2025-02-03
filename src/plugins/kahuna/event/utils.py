# nonebot model
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11 import Event
# import logger
from ..service.log_server import logger

def kahuna_debug_info(event: Event, args: Message, command: str):
    # debug info
    args_text = args.extract_plain_text()
    user_qq = int(event.get_user_id())
    logger.debug(f"init info complete\n"
                 f"  user_qq: {user_qq}\n"
                 f"  args_list: {args_text}\n"
                 f"  command: {command}\n")

    return args_text, user_qq