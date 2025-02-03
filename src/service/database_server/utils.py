

from .connect import db
from .model import MODEL_LIST

def create_default_table():
    need_create_model = []
    for model in MODEL_LIST:
        if not model.table_exists():
            need_create_model.append(model)
    db.create_tables(need_create_model)

def drop_table(table_name):
    with db.atomic():
        db.execute_sql(f'DROP TABLE IF EXISTS "{table_name}"')

    return "\n".join(db.get_tables())

def drop_all_table():
    table_list = db.get_tables()
    with db.atomic():
        for table in table_list:
            db.drop_tables(table)

def get_tables():
    return db.get_tables()