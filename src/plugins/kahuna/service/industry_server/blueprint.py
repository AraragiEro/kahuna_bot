from functools import lru_cache

from ..sde_service.database import IndustryActivityMaterials, IndustryActivityProducts

class BPManager:
    @classmethod
    @lru_cache(maxsize=1000)
    def get_bp_materials(cls, type_id: int) -> dict:
        material_search = (
            IndustryActivityMaterials
                .select(IndustryActivityMaterials.materialTypeID, IndustryActivityMaterials.quantity)
                .join(IndustryActivityProducts,
                      on=(IndustryActivityMaterials.blueprintTypeID==IndustryActivityProducts.blueprintTypeID))
                .where((IndustryActivityProducts.productTypeID==type_id) &
                       ((IndustryActivityMaterials.activityID == 1) | (IndustryActivityMaterials.activityID == 11)))
        )
        return {material.materialTypeID: material.quantity for material in material_search}

    @classmethod
    @lru_cache(maxsize=1000)
    def get_bp_product_quantity(cls, type_id: int) -> int:
        try:
            product_quantity = IndustryActivityProducts.select(IndustryActivityProducts.quantity).where(
                IndustryActivityProducts.productTypeID == type_id
            ).get().quantity
        except IndustryActivityProducts.DoesNotExist:
            product_quantity = 1  # 或者你想要的默认值

        return product_quantity

    @classmethod
    @lru_cache(maxsize=1000)
    def check_product_id_existence(cls, product_type_id: int) -> bool:
        return IndustryActivityProducts.select().where(IndustryActivityProducts.productTypeID == product_type_id).exists()

    @classmethod
    @lru_cache(maxsize=1000)
    def get_production_time(cls, product_id: int) -> int:
        """
        获取指定产品的制造活动时间（秒）
        
        参数：
            product_id (int): 产品ID
            
        返回：
            int: 制造活动时间，单位秒。如果未找到返回0
        """
        details = cls.get_blueprint_details(product_id)
        if details is None:
            return 0
            
        for activity in details['activities']:
            if activity['activityID'] == 1 or activity['activityID'] == 11:  # 制造活动
                return activity['time']
        return 0

    @classmethod
    @lru_cache(maxsize=1000)
    def get_chunk_runs(cls, product_id: int) -> int:
        """
        计算单个蓝图每日可完成的制造流程数
        
        参数：
            product_id (int): 产品ID
            
        返回：
            int: 每日可完成的制造流程数
        """
        production_time = cls.get_production_time(product_id)
        if production_time <= 0:
            return 0
        return max(1, 86400 // production_time)  # 86400秒 = 1天

    @classmethod
    @lru_cache(maxsize=1000)
    def get_blueprint_details(cls, product_id: int) -> dict:
        """
        根据产品ID返回蓝图的详细信息字典。
        
        参数：
            product_id (int): 产品的ID
        
        返回：
            dict: 包含蓝图详细信息的字典，包括基本属性、材料和活动时间
        """
        from ..sde_service.database import InvTypes, IndustryActivityMaterials, IndustryActivities
        
        blueprint_details = {
            'product_info': {},
            'materials': [],
            'activities': []
        }
        
        try:
            # 获取产品基本信息
            product = InvTypes.get(InvTypes.typeID == product_id)
            blueprint_details['product_info'] = {
                'typeID': product.typeID,
                'typeName': product.typeName,
                'description': product.description,
                'mass': product.mass,
                'volume': product.volume,
                'basePrice': product.basePrice
            }
            
            # 获取所有与该产品相关的蓝图活动材料
            materials = IndustryActivityMaterials.select(
                    IndustryActivityMaterials.materialTypeID,
                    IndustryActivityMaterials.quantity  # 
                ).join(
                IndustryActivityProducts,
                on=(IndustryActivityMaterials.blueprintTypeID == 
                    IndustryActivityProducts.blueprintTypeID)
            ).where((IndustryActivityProducts.productTypeID == product_id) &
                    ((IndustryActivityMaterials.activityID == 1) | (IndustryActivityMaterials.activityID == 11)))
            
            for material in materials:
                blueprint_details['materials'].append({
                    'material_typeID': material.materialTypeID,
                    'quantity': material.quantity
                })
            
            # 获取所有与该产品相关的蓝图活动信息
            # 首先通过 IndustryActivityProducts 获取 blueprintTypeID
            blueprint_type_id = IndustryActivityProducts.select(
                IndustryActivityProducts.blueprintTypeID
            ).where(
                IndustryActivityProducts.productTypeID == product_id
            ).get().blueprintTypeID
            
            # 然后使用 blueprintTypeID 查询 IndustryActivities
            activities = IndustryActivities.select(
                IndustryActivities.activityID,
                IndustryActivities.time
            ).where(
                IndustryActivities.blueprintTypeID == blueprint_type_id
            )
            
            for activity in activities:
                blueprint_details['activities'].append({
                    'activityID': activity.activityID,
                    'time': activity.time
                })
                
        except Exception as e:
            print(f"Error retrieving blueprint details: {e}")
            return None
        
        return blueprint_details
