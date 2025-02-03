from functools import lru_cache
from pydantic import BaseModel

from ..sde_service.database import InvTypes, InvGroups, InvCategories
from ..sde_service.database import MetaGroups

def get_t2_ship() -> list:
    t2_search = (
        InvTypes.select(InvTypes.typeName)
        .join(InvGroups, on=(InvTypes.groupID == InvGroups.groupID))
        .join(InvCategories, on=(InvGroups.categoryID==InvCategories.categoryID))
        .where(InvCategories.categoryName == "Ship")
        .switch(InvTypes)
        .join(MetaGroups, on=(InvTypes.metaGroupID == MetaGroups.metaGroupID))
        .where(MetaGroups.nameID == "Tech II")
    )

    result = [type.typeName for type in t2_search]

    return result

@lru_cache(maxsize=1000)
def get_invtpye_node_by_id(invtpye_id: int) -> InvTypes:
    try:
        return InvTypes.get(InvTypes.typeID == invtpye_id)
    except InvTypes.DoesNotExist:
        return None

@lru_cache(maxsize=1000)
def get_id_by_name(name) -> int:
    try:
        return InvTypes.get(InvTypes.typeName == name).typeID
    except InvTypes.DoesNotExist:
        return None

@lru_cache(maxsize=1000)
def get_name_by_id(type_id) -> str:
    try:
        return InvTypes.get(InvTypes.typeID == type_id).typeName
    except InvTypes.DoesNotExist:
        return None