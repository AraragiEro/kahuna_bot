# # python model
# from datetime import datetime

# # kahuna model
# from ..service.user_server import UserManager

# # import Exception
# from ..utils import KahunaException

# # import logger


# class PermissionChecker(object):
#     admin = SUPERUSER
#     default_permission = GROUP | PRIVATE_FRIEND

#     @staticmethod
#     async def member(event: Event) -> bool:
#         user_qq = int(event.get_user_id())
#         try:
#             user = UserManager().get_user(user_qq)
#             return user.expire_date > datetime.now()
#         except KahunaException as e:
#             return False