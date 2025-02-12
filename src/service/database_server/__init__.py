import os
os.environ["KAHUNA_DB_DIR"] = "F:\WorkSpace\GIT\kahuna_bot\AstrBot\data\plugins\kahuna_bot"

from ..database_server.utils import create_default_table, drop_table, drop_all_table, get_tables

create_default_table()