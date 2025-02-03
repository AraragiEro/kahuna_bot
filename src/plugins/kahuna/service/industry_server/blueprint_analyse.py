from functools import lru_cache
import networkx as nx

from .blueprint import get_bp_materials, get_bp_product_quantity, check_product_id_existence
from .item import get_id_by_name
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

        self.bfs_tree(bfs_queue)

    def bfs_tree(self, bfs_queue: list):
        """
        递归处理生成蓝图节点。
        每个节点代表一种材料，每种target需要的材料存储在子结构
        节点与节点之间的边关系
        """
        while bfs_queue:
            target_id, type_id, quantity = bfs_queue.pop(0)
            self.bp_graph.add_node(target_id)
            if (bp_materials := get_bp_materials(type_id)) is None:
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

    @lru_cache(maxsize=None)
    def calculate_bpnode_quantity(self, typeid: int):
        if typeid not in self.bp_node_quantity_dict:
            self.bp_node_quantity_dict[typeid] = dict()

        in_edge = self.bp_graph.in_edges(typeid, data=True)
        need_cal_edge = [edge for edge in in_edge]

        for edge in need_cal_edge:
            source_id = edge[0]
            target_id = edge[2]["target_id"]
            if target_id not in self.bp_node_quantity_dict[typeid]:
                self.bp_node_quantity_dict[typeid][target_id] = dict()

            # 递归查询
            source_quantity = (1 if source_id == "root" else self.calculate_bpnode_quantity(source_id))
            coefficient = 1
            source_product_quantity = 1 if source_id == "root" else get_bp_product_quantity(source_id)
            source_need_run = source_quantity / source_product_quantity
            source_need_child = edge[2]["quantity"]
            self.bp_node_quantity_dict[typeid][target_id][source_id] = source_need_run * coefficient * source_need_child

        total_quantity = sum([sum(self.bp_node_quantity_dict[typeid][target_id].values()) for target_id in self.bp_node_quantity_dict[typeid].keys()])
        type_product_quantity = get_bp_product_quantity(typeid)

        return roundup(total_quantity, type_product_quantity) if self.cal_type == "work" else total_quantity

    def get_product_ori_materials(self, product: str, quantity: int = 1) -> dict:
        if not check_product_id_existence(get_id_by_name(product)):
            raise KahunaException("物品无蓝图。")
        work_list = [(product, quantity)]
        self.get_work_tree(work_list)

        nodes_without_outgoing_edges = [node for node, degree in self.bp_graph.out_degree() if degree == 0]
        res_dict = {}
        for node in nodes_without_outgoing_edges:
            res_dict[node] = self.calculate_bpnode_quantity(node)
        return res_dict

    def clean_bp_graph(self):
        self.bp_graph.clear()