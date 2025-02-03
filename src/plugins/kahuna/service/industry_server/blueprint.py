from functools import lru_cache

from ..sde_service.database import IndustryActivityMaterials, IndustryActivityProducts

@lru_cache(maxsize=1000)
def get_bp_materials(type_id: int) -> dict:
    material_search = (
        IndustryActivityMaterials
            .select(IndustryActivityMaterials.materialTypeID, IndustryActivityMaterials.quantity)
            .join(IndustryActivityProducts,
                  on=(IndustryActivityMaterials.blueprintTypeID==IndustryActivityProducts.blueprintTypeID))
            .where((IndustryActivityProducts.productTypeID==type_id) &
                   ((IndustryActivityMaterials.activityID == 1) | (IndustryActivityMaterials.activityID == 11)))
    )
    return {material.materialTypeID: material.quantity for material in material_search}

@lru_cache(maxsize=1000)
def get_bp_product_quantity(type_id: int) -> int:
    try:
        product_quantity = IndustryActivityProducts.select(IndustryActivityProducts.quantity).where(
            IndustryActivityProducts.productTypeID == type_id
        ).get().quantity
    except IndustryActivityProducts.DoesNotExist:
        product_quantity = 1  # 或者你想要的默认值

    return product_quantity


@lru_cache(maxsize=1000)
def check_product_id_existence(product_type_id: int) -> bool:
    return IndustryActivityProducts.select().where(IndustryActivityProducts.productTypeID == product_type_id).exists()
