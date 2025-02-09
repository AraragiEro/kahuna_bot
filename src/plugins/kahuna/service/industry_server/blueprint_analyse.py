import networkx as nx
import math

from .blueprint import BPManager #get_bp_materials, get_bp_product_quantity, check_product_id_existence
from ..sde_service.utils import get_id_by_name
from ...utils import roundup, KahunaException

class BpAnalyser():
    bp_node_dict: dict = dict()
    bp_node_hash_set: set = set()
    bp_graph: nx.DiGraph = nx.DiGraph()
    anaed_set = set()
    bp_node_quantity_dict = dict()
    cal_type = "work" # "work"会根据蓝图实际输出计算成本，"cost"则不会，输出的是长期情况下的最小成本
    def __init__(self, cal_type="work"):
        self.cal_type = cal_type

    def get_work_tree(self, work_list: list):
        """
        :param work_list: [(target_id, quantity)]
        :return:
        """
        work_list = [(get_id_by_name(target), quantity) for target, quantity in work_list]
        # queue: [target_id, node_id, quanqity]
        bfs_queue = [(target_id, target_id, 1) for target_id, _ in work_list]

        self.bp_graph.add_node("root")
        self.bp_graph.add_nodes_from([(target_id) for target_id, _ in work_list])
        self.bp_graph.add_edges_from(
            [("root", target_id, {"target_id": target_id, "quantity": quantity})
             for target_id, quantity in work_list])

        self.bfs_bp_tree(bfs_queue)

    def bfs_bp_tree(self, bfs_queue: list):
        """
        递归处理生成蓝图节点。
        每个节点代表一种材料，每种target需要的材料存储在子结构
        节点与节点之间的边关系
        """
        while bfs_queue:
            target_id, type_id, quantity = bfs_queue.pop(0)
            self.bp_graph.add_node(target_id)
            if (bp_materials := BPManager.get_bp_materials(type_id)) is None:
                self.anaed_set.add(type_id)
                continue
            self.bp_graph.add_nodes_from([child_id for child_id in bp_materials.keys()])
            self.bp_graph.add_edges_from(
                [(type_id, child_id, {"target_id": target_id, "quantity": quantity})
                 for child_id, quantity in bp_materials.items()]
            )

            bfs_queue = bfs_queue + [(target_id, child_id, quantity) for child_id, quantity in bp_materials.items()
                                     if child_id not in self.anaed_set]
            self.anaed_set.update(bp_materials.keys())

    def calculate_ori_bpnode_quantity(self, typeid: int, cache_dict: dict):
        if typeid in cache_dict:
            return cache_dict[typeid]
        if typeid not in self.bp_node_quantity_dict:
            self.bp_node_quantity_dict[typeid] = dict()

        need_cal_edge = [edge for edge in self.bp_graph.in_edges(typeid, data=True)]

        for edge in need_cal_edge:
            source_id = edge[0]
            target_id = edge[2]["target_id"]
            if target_id not in self.bp_node_quantity_dict[typeid]:
                self.bp_node_quantity_dict[typeid][target_id] = dict()

            # 定义材料效率占位符
            coefficient = 1

            # 递归查询
            source_quantity = (1 if source_id == "root" else self.calculate_ori_bpnode_quantity(source_id, cache_dict))

            source_product_quantity = 1 if source_id == "root" else BPManager.get_bp_product_quantity(source_id)
            source_need_run = source_quantity / source_product_quantity
            source_need_child = edge[2]["quantity"]
            target_need_from_source = source_need_run * coefficient * source_need_child
            self.bp_node_quantity_dict[typeid][target_id][source_id] = target_need_from_source

        total_quantity = sum([sum(self.bp_node_quantity_dict[typeid][target_id].values()) for target_id in self.bp_node_quantity_dict[typeid].keys()])
        type_product_quantity = BPManager.get_bp_product_quantity(typeid)

        return roundup(total_quantity, type_product_quantity) if self.cal_type == "work" else total_quantity

    def calculate_work_bpnode_quantity(self, typeid: int, cache_dict: dict):
        """
        计算工作蓝图节点数量（实际执行模式）
        
        参数：
            typeid (int): 蓝图类型ID
        """
        if typeid in cache_dict:
            return cache_dict[typeid]
        DAYS_PER_CYCLE = 1  # 按天计算生产周期
        
        # production_time = BPManager.get_production_time(typeid)
        # if production_time <= 0:
        #     return 0

        if typeid not in self.bp_node_quantity_dict:
            self.bp_node_quantity_dict[typeid] = dict()

        need_cal_edge = [edge for edge in self.bp_graph.in_edges(typeid, data=True)]

        total_quantity = 0
        for edge in need_cal_edge:
            source_id = edge[0]
            target_id = edge[2]["target_id"]
            if target_id not in self.bp_node_quantity_dict[typeid]:
                self.bp_node_quantity_dict[typeid][target_id] = dict()

            # 定义材料效率占位符
            coefficient = 1

            # 递归查询源材料需求（按工作模式计算）
            source_quantity = (1 if source_id == "root" else self.calculate_work_bpnode_quantity(source_id, cache_dict))
            
            # 获取生产参数
            source_product_quantity = 1 if source_id == "root" else BPManager.get_bp_product_quantity(source_id)
            chunk_runs = 1 if source_id == "root" else BPManager.get_chunk_runs(source_id)  # 每轮工作最大流程数
            
            # 计算实际需要的生产流程数（向上取整）
            total_runs_needed = math.ceil(source_quantity / source_product_quantity)
            
            # 计算完整生产轮数和最后一轮的流程数
            full_chunks = total_runs_needed // chunk_runs
            last_chunk_runs = total_runs_needed % chunk_runs
            
            # 处理完整天数
            target_need_from_source_total = 0
            if full_chunks > 0:
                daily_material = edge[2]["quantity"] * chunk_runs * coefficient
                for _ in range(full_chunks):
                    target_need_from_source_total += math.ceil(daily_material)
            
            # 处理最后一天
            if last_chunk_runs > 0:
                last_day_material = edge[2]["quantity"] * last_chunk_runs * coefficient
                target_need_from_source_total += math.ceil(last_day_material)

            self.bp_node_quantity_dict[typeid][target_id][source_id] = target_need_from_source_total
            total_quantity += target_need_from_source_total

        # total_quantity = sum([sum(self.bp_node_quantity_dict[typeid][target_id].values())
        #                     for target_id in self.bp_node_quantity_dict[typeid].keys()])
        type_product_quantity = BPManager.get_bp_product_quantity(typeid)
        res = roundup(total_quantity, type_product_quantity) if self.cal_type == "work" else total_quantity
        cache_dict[typeid] = res
        return res

    def get_product_ori_materials(self, product: str, quantity: int = 1) -> dict:
        if not BPManager.check_product_id_existence(get_id_by_name(product)):
            raise KahunaException("物品无蓝图。")
        work_list = [(product, quantity)]
        self.get_work_tree(work_list)

        nodes_without_outgoing_edges = [node for node, degree in self.bp_graph.out_degree() if degree == 0]
        res_dict = {}
        cache_dict = dict()
        for node in nodes_without_outgoing_edges:
            res_dict[node] = self.calculate_ori_bpnode_quantity(node, cache_dict)
        return res_dict

    def get_product_work_materials(self, product: str, quantity: int = 1) -> dict:
        if not BPManager.check_product_id_existence(get_id_by_name(product)):
            raise KahunaException("物品无蓝图。")
        work_list = [(product, quantity)]
        self.get_work_tree(work_list)

        nodes_without_outgoing_edges = [node for node, degree in self.bp_graph.out_degree() if degree == 0]
        res_dict = {}
        cache_dict = dict()
        for node in nodes_without_outgoing_edges:
            res_dict[node] = self.calculate_work_bpnode_quantity(node, cache_dict)
        return res_dict

    def clean_bp_graph(self):
        self.bp_graph.clear()
