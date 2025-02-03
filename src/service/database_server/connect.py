from peewee import SqliteDatabase

from ...utils import KahunaException
from ..config_server.config import config

if config['APP']['DBTYPE'] == 'sqlite' and config['SQLITEDB']['DATADB']:
    db = SqliteDatabase(config['SQLITEDB']['DATADB'], pragmas={
        'journal_mode': 'wal',  # 启用 WAL 模式
        'cache_size': -1024 * 64,  # 调整缓存大小，单位为 KB
        'synchronous': 0  # 提高性能：异步写日志
    }, timeout=120)
else:
    raise KahunaException("bot db open failed")

db.connect()