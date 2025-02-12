from peewee import SqliteDatabase
import os

from ...utils import KahunaException

if "KAHUNA_DB_DIR" not in os.environ:
    raise KahunaException("KAHUNA_DB_DIR environment variable not set.")
db_dir = os.path.join(os.environ["KAHUNA_DB_DIR"], "kahuna.db")

db = SqliteDatabase(db_dir)

db.connect()