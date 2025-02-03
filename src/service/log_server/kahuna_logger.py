import logging

from astrbot.core import logger as astrbot_logger

# 创建一个名为 'project_logger' 的 logger
logger = logging.getLogger('kahuna_bot')

# 设置全局级别为 DEBUG
logger.setLevel(logging.DEBUG)

# 创建一个输出到控制台的处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 设置此处理器的日志级别

# 创建一个输出到文件的处理器
file_handler = logging.FileHandler('project.log')
file_handler.setLevel(logging.DEBUG)  # 设置此处理器的日志级别

# 创建一个格式化器并添加到处理器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到 logger
logger.addHandler(console_handler)
# logger.addHandler(file_handler)

logger = astrbot_logger
