import configparser
import os

from ..log_server import logger

# 获取当前脚本文件的完整路径
script_file_path = os.path.abspath(__file__)

# 获取脚本文件所在目录
script_dir = os.path.dirname(script_file_path)

# 初始化解析器
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, '../../../config.ini'))

# 访问配置内容
# print(config['DEFAULT']['AppName'])  # 输出：MyApp
# print(config['Database']['Host'])  # 输出：localhost

# 转换为字典
# db_config = dict(config['Database'])
# print(db_config)  # 输出：{'host': 'localhost', 'port': '5432', 'user': 'admin', 'password': 'secret'}

logger.info("Config server loaded.")
logger.info(f"database type: {config['APP']['DBTYPE']}")