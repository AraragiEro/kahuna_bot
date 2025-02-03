from peewee import SqliteDatabase
from peewee import Model
from peewee import FloatField, DecimalField, CharField, TextField, DateTimeField, BooleanField, IntegerField, DoubleField
from peewee import BigIntegerField
from peewee import SQL
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
    main_character_id = IntegerField()
__all__.append('User')
MODEL_LIST.append(User)

class UserData(BaseModel):
    user_qq = IntegerField(unique=True)
    user_data = TextField()
    class Meta:
        table_name = 'user_data'
__all__.append('UserData')
MODEL_LIST.append(UserData)

class Character(BaseModel):
    character_id = IntegerField(unique=True)
    character_name = TextField()
    QQ = IntegerField()
    create_date = DateTimeField()
    token = TextField()
    refresh_token = TextField()
    expires_date = DateTimeField()
    corp_id = IntegerField()
    director = BooleanField()

    class Meta:
        table_name = 'character'
__all__.append('Character')
MODEL_LIST.append(Character)

class Structure(BaseModel):
    structure_id = IntegerField(unique=True)
    name = CharField()
    owner_id = IntegerField()
    solar_system_id = IntegerField()
    type_id = IntegerField()
    system = IntegerField()
    mater_rig_level = IntegerField(null=True)
    time_rig_level = IntegerField(null=True)
    class Meta:
        table_name = 'structure'
__all__.append('Structure')
MODEL_LIST.append(Structure)

class AssetContainer(BaseModel):
    asset_location_id = IntegerField()
    asset_location_type = CharField()
    structure_id = IntegerField()
    solar_system_id = IntegerField()
    asset_name = TextField()
    asset_owner_id = IntegerField()
    asset_owner_type = CharField()
    asset_owner_qq = IntegerField()
    tag = CharField(null=True)

    class Meta:
        table_name = 'asset_container'
        constraints = [SQL('UNIQUE(asset_location_id, asset_owner_qq)')]
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


class IndustryJobs(BaseModel):
    activity_id = IntegerField()
    blueprint_id = BigIntegerField()
    blueprint_location_id = BigIntegerField()
    blueprint_type_id = IntegerField()
    completed_character_id = IntegerField(null=True)
    completed_date = DateTimeField(null=True)
    cost = DoubleField(null=True)
    duration = IntegerField()
    end_date = DateTimeField()
    facility_id = BigIntegerField()
    installer_id = IntegerField()
    job_id = IntegerField()
    licensed_runs = IntegerField(null=True)
    location_id = BigIntegerField() # station_id in character api return
    output_location_id = BigIntegerField()
    pause_date = DateTimeField(null=True)
    probability = FloatField(null=True)
    product_type_id = IntegerField(null=True)
    runs = IntegerField()
    start_date = DateTimeField()
    status = CharField()
    successful_runs = IntegerField(null=True)

    owner_id = IntegerField()

    class Meta:
        table_name = 'industry_jobs'
__all__.append(IndustryJobs.__name__)
MODEL_LIST.append(IndustryJobs)

class IndustryJobsCache(BaseModel):
    activity_id = IntegerField()
    blueprint_id = BigIntegerField()
    blueprint_location_id = BigIntegerField()
    blueprint_type_id = IntegerField()
    completed_character_id = IntegerField(null=True)
    completed_date = DateTimeField(null=True)
    cost = DoubleField(null=True)
    duration = IntegerField()
    end_date = DateTimeField()
    facility_id = BigIntegerField()
    installer_id = IntegerField()
    job_id = IntegerField()
    licensed_runs = IntegerField(null=True)
    location_id = BigIntegerField() # station_id in character api return
    output_location_id = BigIntegerField()
    pause_date = DateTimeField(null=True)
    probability = FloatField(null=True)
    product_type_id = IntegerField(null=True)
    runs = IntegerField()
    start_date = DateTimeField()
    status = CharField()
    successful_runs = IntegerField(null=True)

    owner_id = IntegerField()
    class Meta:
        table_name = 'industry_jobs_cache'
__all__.append(IndustryJobsCache.__name__)
MODEL_LIST.append(IndustryJobsCache)

class SystemCost(BaseModel):
    solar_system_id = IntegerField(primary_key=True)
    manufacturing = FloatField(null=True)
    researching_time_efficiency = FloatField(null=True)
    researching_material_efficiency = FloatField(null=True)
    copying = FloatField(null=True)
    invention = FloatField(null=True)
    reaction = FloatField(null=True)

    class Meta:
        table_name = "system_cost"
__all__.append(SystemCost.__name__)
MODEL_LIST.append(SystemCost)

class SystemCostCache(BaseModel):
    solar_system_id = IntegerField(primary_key=True)
    manufacturing = FloatField(null=True)
    researching_time_efficiency = FloatField(null=True)
    researching_material_efficiency = FloatField(null=True)
    copying = FloatField(null=True)
    invention = FloatField(null=True)
    reaction = FloatField(null=True)

    class Meta:
        table_name = "system_cost_cache"
__all__.append(SystemCostCache.__name__)
MODEL_LIST.append(SystemCostCache)

class BlueprintAsset(BaseModel):
    item_id = BigIntegerField(primary_key=True)
    location_flag = CharField()
    location_id = BigIntegerField()
    material_efficiency = IntegerField()
    quantity = IntegerField()
    runs = IntegerField()
    time_efficiency = IntegerField()
    type_id = IntegerField()

    owner_id = IntegerField()
    owner_type = CharField()
    class Meta:
        table_name = "blueprint_asset"
__all__.append(BlueprintAsset.__name__)
MODEL_LIST.append(BlueprintAsset)


class BlueprintAssetCache(BaseModel):
    item_id = BigIntegerField(primary_key=True)
    location_flag = CharField()
    location_id = BigIntegerField()
    material_efficiency = IntegerField()
    quantity = IntegerField()
    runs = IntegerField()
    time_efficiency = IntegerField()
    type_id = IntegerField()

    owner_id = IntegerField()
    owner_type = CharField()
    class Meta:
        table_name = "blueprint_asset_cache"
__all__.append(BlueprintAssetCache.__name__)
MODEL_LIST.append(BlueprintAssetCache)

class InvTypeMap(BaseModel):
    maped_type = CharField(unique=True)
    target_type = CharField()
    class Meta:
        table_name = "inv_type_map"
__all__.append(InvTypeMap.__name__)
MODEL_LIST.append(InvTypeMap)

class Matcher(BaseModel):
    matcher_name = CharField(unique=True)
    user_qq = IntegerField()
    matcher_type = CharField()
    matcher_data = TextField()
    class Meta:
        table_name = "matcher"
__all__.append(Matcher.__name__)
MODEL_LIST.append(Matcher)

class MarketPrice(BaseModel):
    adjusted_price = IntegerField(null=True)
    average_price = IntegerField(null=True)
    type_id = IntegerField(primary_key=True)
    class Meta:
        table_name = "market_price"
__all__.append(MarketPrice.__name__)
MODEL_LIST.append(MarketPrice)

class MarketPriceCache(BaseModel):
    adjusted_price = IntegerField(null=True)
    average_price = IntegerField(null=True)
    type_id = IntegerField(primary_key=True)
    class Meta:
        table_name = "market_price_cache"
__all__.append(MarketPriceCache.__name__)
MODEL_LIST.append(MarketPriceCache)

class MarketHistory(BaseModel):
    region_id = IntegerField()
    type_id = IntegerField()
    date = DateTimeField()
    average = IntegerField()
    highest = IntegerField()
    lowest = IntegerField()
    order_count = IntegerField()
    volume = IntegerField()
    class Meta:
        table_name = "market_history"
        indexes = (
            (('region_id', 'type_id', 'date'), True),
        )
__all__.append(MarketHistory.__name__)
MODEL_LIST.append(MarketHistory)