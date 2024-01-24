import json
from typing import Dict, List

from topt.topt import TreeNode, NodeTag, Decision, Move, State
import topt.topt as topt


def add_expanding_spr_edges_to_tree_node_json(tree_node: TreeNode, tree: Dict, moves: List[Move]):
    for move in moves:
        source_lower = topt.find_common_ancestor(tree_node, move.source)
        source_upper = topt.get_parent(tree_node, source_lower)
        source = f"{str(source_lower.data.label)}_{str(source_upper.data.label)}"
        target_lower = topt.find_common_ancestor(tree_node, move.target)
        target_upper = topt.get_parent(tree_node, target_lower)
        target = f"{str(target_lower.data.label)}_{str(target_upper.data.label)}"
        tree["nodes"].append(
            {
                "data": {
                    "id": source
                },
                "classes": "node, sprNode"
            }
        )

        tree["nodes"].append(
            {
                "data": {
                    "id": target
                },
                "classes": "node, sprNode"
            }
        )

        tree["edges"].append(
            {
                "data": {
                    "source": str(source),
                    "target": str(target)
                },
                "classes": "sprEdge"
            }
        )
    return tree


def add_expanding_spr_edges_to_tree_node_json_type_2(tree_node: TreeNode, tree: Dict, moves: List[Move]):
    for move in moves:
        source_lower = topt.find_common_ancestor(tree_node, move.source)
        source_upper = topt.get_parent(tree_node, source_lower)
        source = f"{str(source_lower.data.label)}_{str(source_upper.data.label)}"
        target_lower = topt.find_common_ancestor(tree_node, move.target)
        target_upper = topt.get_parent(tree_node, target_lower)
        target = f"{target_upper.data.label}@d"  # for this type we go directly to this node in the js need the d to distinguish from the node in the tree
        tree["nodes"].append(
            {
                "data": {
                    "id": source
                },
                "classes": "node sourceNode"
            }
        )

        tree["nodes"].append(
            {
                "data": {
                    "id": target
                },
                "classes": "node targetNode"
            }
        )

        tree["edges"].append(
            {
                "data": {
                    "source": str(source),
                    "target": str(target)
                },
                "classes": "sprEdge"
            }
        )
    return tree


def build_tree_node_json(tree_node: TreeNode):
    all_nodes = topt.get_all_nodes(topt.label_tree(tree_node, 0))
    tree = {
        "nodes": [],
        "edges": []
    }

    for node in all_nodes:
        tree["nodes"].append(
            {
                "data": {
                    "id": str(node.data.label)
                },
                "classes": "node " + "leaf" if node.data.tag == NodeTag.LEAF else "inserted" if node.data.tag == NodeTag.INSERTED else "node"
            }
        )

    all_edges = []
    # TODO:Fix this function
    topt.get_all_edges_as_tuples(tree_node, all_edges)

    for source, target in all_edges:
        tree["edges"].append(
            {
                "data": {
                    "source": str(source),
                    "target": str(target)
                },
                # "classes": "node " + "leaf" if node.data.tag == NodeTag.LEAF else ""
            }
        )

    return tree


def build_decision_json(decision: Decision):
    all_nodes = topt.get_all_nodes(decision)
    tree = {
        "nodes": [],
        "edges": []
    }

    for node in all_nodes:
        tree["nodes"].append(
            {
                "data": {
                    "id": str(node.label)
                },
                "classes": node.status.state.value + " node"
            }
        )

    all_edges = []
    # TODO:Fix this function
    topt.get_all_edges_as_tuples(decision, all_edges)

    for source, target in all_edges:
        tree["edges"].append(
            {
                "data": {
                    "source": str(source),
                    "target": str(target)
                },
                # "classes": "node " + "leaf" if node.data.tag == NodeTag.LEAF else ""
            }
        )

    return tree


def traverse_decisions_get_all(decision_root: Decision, decision_dict: Dict):
    if not decision_root.children:
        decision_dict[str(decision_root.label)] = extract_decision(decision_root)
        return
    else:
        decision_dict[str(decision_root.label)] = extract_decision(decision_root)
        for child in decision_root.children:
            traverse_decisions_get_all(child, decision_dict)
        return


def traverse_decisions(decision_root: Decision):
    if not decision_root.children:
        return {"decision": extract_decision(decision_root), "children": []}
    else:
        children = []
        for child in decision_root.children:
            children.append(traverse_decisions(child))
        return {"decision": extract_decision(decision_root), "children": children}


def extract_decision(decision: Decision):
    json = {"data": [], }
    for record in decision.data:
        tree_node_with_outgroup = record.node  # , topt.create_leaf_tree_node("X"))
        tree_json_no_spr = topt.build_tree_node_json(tree_node_with_outgroup)

        if decision.status.state in [State.EXPANDING, State.COMPARED]:
            tree_json_no_spr = topt.add_expanding_spr_edges_to_tree_node_json(tree_node_with_outgroup, tree_json_no_spr,
                                                                              record.moves.possible)
        elif decision.status.state in [State.FINISH]:
            tree_json_no_spr = topt.add_expanding_spr_edges_to_tree_node_json_type_2(tree_node_with_outgroup, tree_json_no_spr,
                                                                              # could do type2 here
                                                                              record.moves.applied)

        json["data"].append({"tree": tree_json_no_spr,
                             "moves": record.moves.to_dict(),
                             })
        json["state"] = decision.status.state.value
        json["value"] = decision.status.value
    return json


"""def build_tree_node_json(tree_node: TreeNode):
    all_nodes = topt.get_all_nodes(topt.label_tree(tree_node, 0))
    tree = {
        "nodes": [],
        "edges": []
    }

    for node in all_nodes:
        tree["nodes"].append(
            {
                "data": {
                    "id": str(node.data.label)
                },
                "classes": "node " + "leaf" if node.data.tag == NodeTag.LEAF else "inserted" if node.data.tag == NodeTag.INSERTED else "node"
            }
        )

    all_edges = []
    topt.get_all_edges_as_tuples(tree_node, all_edges)

    for source, target in all_edges:
        new_node_id = str(source) + "_" + str(target) + "_link"
        tree["nodes"].append(
            {
                "data": {
                    "id": new_node_id
                },
                "classes": "node link"
            }
        )
        tree["edges"].append(
            {
                "data": {
                    "source": str(source),
                    "target": new_node_id
                },
            }
        )
        tree["edges"].append(
            {
                "data": {
                    "source": new_node_id,
                    "target": str(target)
                },
            }
        )

    return tree"""
