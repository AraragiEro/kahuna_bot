from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField, IntegerField, TextField, FloatField

db = SqliteDatabase('sde.sqlite')

class BaseModel(Model):
    class Meta:
        database = db

# 所有的type信息
class InvTypes(BaseModel):
    typeID = IntegerField(primary_key=True)
    groupID = IntegerField(null=True)
    typeName = TextField(null=True)
    description = TextField(null=True)
    mass = FloatField(null=True)
    volume = FloatField(null=True)
    packagedVolume = FloatField(null=True)
    capacity = FloatField(null=True)
    portionSize = IntegerField(null=True)
    factionID = IntegerField(null=True)
    raceID = IntegerField(null=True)
    basePrice = FloatField(null=True)
    published = IntegerField(null=True)
    marketGroupID = IntegerField(null=True)
    graphicID = IntegerField(null=True)
    radius = FloatField(null=True)
    iconID = IntegerField(null=True)
    soundID = IntegerField(null=True)
    sofFactionName = TextField(null=True)
    sofMaterialSetID = IntegerField(null=True)
    metaGroupID = IntegerField(null=True)
    variationparentTypeID = IntegerField(null=True)

    class Meta:
        table_name = 'invTypes'

# 蓝图原料信息
class IndustryActivityMaterials(BaseModel):
    blueprintTypeID = IntegerField()
    activityID = IntegerField()
    materialTypeID = IntegerField()
    quantity = IntegerField()

    class Meta:
        table_name = 'industryActivityMaterials'

# 蓝图产品信息
class IndustryActivityProducts(BaseModel):
    blueprintTypeID = IntegerField()
    activityID = IntegerField()
    productTypeID = IntegerField()
    quantity = IntegerField()
    probability = FloatField()

    class Meta:
        table_name = 'industryActivityProducts'

# 元组id信息
class MetaGroups(BaseModel):
    metaGroupID = IntegerField(primary_key=True)
    descriptionID = TextField(null=True)
    iconID = IntegerField(null=True)
    iconSuffix = TextField(null=True)
    nameID = TextField(null=True)

    class Meta:
        table_name = 'metaGroups'

# 组id对应
class InvGroups(BaseModel):
    groupID = IntegerField(primary_key=True)
    categoryID = IntegerField(null=True)
    groupName = TextField(null=True)
    iconID = IntegerField(null=True)
    useBasePrice = IntegerField(null=True)
    anchored = IntegerField(null=True)
    anchorable = IntegerField(null=True)
    fittableNonSingleton = IntegerField(null=True)
    published = IntegerField(null=True)

    class Meta:
        table_name = 'invGroups'

# 属性id对应
class InvCategories(BaseModel):
    categoryID = IntegerField(primary_key=True)
    categoryName = TextField(null=True)
    published = IntegerField(null=True)
    iconID = IntegerField(null=True)

    class Meta:
        table_name = 'invCategories'

class MapSolarSystems(BaseModel):
    solarSystemID = IntegerField(primary_key=True)
    solarSystemName = CharField(max_length=100)
    regionID = IntegerField()
    constellationID = IntegerField()
    x = FloatField()
    y = FloatField()
    z = FloatField()
    x_Min = FloatField()
    x_Max = FloatField()
    y_Min = FloatField()
    y_Max = FloatField()
    z_Min = FloatField()
    z_Max = FloatField()
    luminosity = FloatField()
    border = IntegerField()
    corridor = IntegerField()
    fringe = IntegerField()
    hub = IntegerField()
    international = IntegerField()
    regional = IntegerField()
    security = FloatField()
    factionID = IntegerField()
    radius = FloatField()
    sunTypeID = IntegerField()
    securityClass = CharField(max_length=2)
    solarSystemNameID = IntegerField()
    visualEffect = CharField()
    descriptionID = IntegerField()

    class Meta:
        table_name = 'mapSolarSystems'

db.connect()