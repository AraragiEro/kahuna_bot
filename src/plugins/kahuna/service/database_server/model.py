from peewee import SqliteDatabase
from peewee import Model
from peewee import FloatField, DecimalField, CharField, TextField, DateTimeField, BooleanField, IntegerField
from peewee import BigIntegerField
from .connect import db

__all__ = []

MODEL_LIST = []

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_qq = IntegerField(unique=True)
    create_date = DateTimeField()
    expire_date = DateTimeField()
__all__.append('User')
MODEL_LIST.append(User)

class Character(BaseModel):
    character_id = IntegerField(unique=True)
    character_name = TextField()
    QQ = IntegerField()
    create_date = DateTimeField()
    token = TextField()
    refresh_token = TextField()
    expires_date = DateTimeField()

    class Meta:
        table_name = 'character'
__all__.append('Character')
MODEL_LIST.append(Character)

class Structure(BaseModel):
    struct_id = IntegerField(unique=True)
    struct_material_ex = FloatField()
    struct_time_ex = FloatField()
    struct_loacation_system = IntegerField()
    class Meta:
        table_name = 'structure'
__all__.append('Structure')
MODEL_LIST.append(Structure)

class AssetContainer(BaseModel):
    asset_location_id = IntegerField(unique=True)
    structure_id = IntegerField()
    asset_name = TextField()
    asset_owner_qq = IntegerField()
    class Meta:
        table_name = 'asset_container'
__all__.append(AssetContainer.__name__)
MODEL_LIST.append(AssetContainer)

# esi_cache
class Asset(BaseModel):
    asset_type = IntegerField()
    owner_id = IntegerField()
    is_blueprint_copy = BooleanField()
    is_singleton = BooleanField()
    item_id = BigIntegerField()
    location_flag = CharField()
    location_id = BigIntegerField()
    location_type = CharField()
    quantity = IntegerField()
    type_id = IntegerField()
    class Meta:
        table_name = 'asset'
__all__.append(Asset.__name__)
MODEL_LIST.append(Asset)

class AssetCache(BaseModel):
    asset_type = IntegerField()
    owner_id = IntegerField()
    is_blueprint_copy = BooleanField()
    is_singleton = BooleanField()
    item_id = BigIntegerField()
    location_flag = CharField()
    location_id = BigIntegerField()
    location_type = CharField()
    quantity = IntegerField()
    type_id = IntegerField()
    class Meta:
        table_name = 'asset_cache'
__all__.append(AssetCache.__name__)
MODEL_LIST.append(AssetCache)

class AssetOwner(BaseModel):
    asset_owner_qq = IntegerField()
    asset_owner_id = IntegerField()
    asset_type = CharField()
    asset_access_character_id = IntegerField()
    class Meta:
        table_name = 'asset_owner'
__all__.append(AssetOwner.__name__)
MODEL_LIST.append(AssetOwner)

class MarketOrder(BaseModel):
    duration = IntegerField()
    is_buy_order = BooleanField()
    issued = DateTimeField()
    location_id = IntegerField()
    min_volume = IntegerField()
    order_id = DecimalField()
    price = DecimalField()
    range = CharField()
    system_id = IntegerField(null=True)
    type_id = IntegerField()
    volume_remain = IntegerField()
    volume_total = IntegerField()

    class Meta:
        table_name = 'market_order'
__all__.append(MarketOrder.__name__)
MODEL_LIST.append(MarketOrder)

class MarketOrderCache(BaseModel):
    duration = IntegerField()
    is_buy_order = BooleanField()
    issued = DateTimeField()
    location_id = IntegerField()
    min_volume = IntegerField()
    order_id = DecimalField()
    price = DecimalField()
    range = CharField()
    system_id = IntegerField(null=True)
    type_id = IntegerField()
    volume_remain = IntegerField()
    volume_total = IntegerField()

    class Meta:
        table_name = 'market_order_cache'
__all__.append(MarketOrderCache.__name__)
MODEL_LIST.append(MarketOrderCache)