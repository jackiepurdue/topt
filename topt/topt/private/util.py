import uuid
from typing import Tuple, Optional, List

from topt.topt.data import TreeNode, NodeData, NodeTag
import topt.topt as topt

def generate_newick(node: TreeNode) -> str:
    if not node.children:
        return node.data.label
    children_newick = ",".join(generate_newick(child) for child in node.children)
    if node.data.label:
        return f"({children_newick}){node.data.label}"
    else:
        return f"({children_newick})"


def find_parent_with_child_label(tree_node: TreeNode, target_label: str, parent_tree_node: TreeNode = None) -> TreeNode:
    if parent_tree_node and tree_node.data.label == target_label:
        return parent_tree_node
    for child in tree_node.children:
        result = find_parent_with_child_label(child, target_label, tree_node)
        if result:
            return result
    return None


def label_tree(tree_node: TreeNode, label_counter: int) -> (TreeNode, int):
    if not tree_node.children:
        if tree_node.data.label == "":
            return TreeNode(
                NodeData(
                    f"{label_counter}",
                    tree_node.data.value,
                    tree_node.data.tag
                )
            ), label_counter
        else:
            return TreeNode(
                NodeData(
                    tree_node.data.label,
                    tree_node.data.value,
                    tree_node.data.tag
                )
            ), label_counter
    updated_children = []
    # count = label_counter
    count = label_counter
    for child in tree_node.children:
        count = count + 1
        tree_counter_pair = label_tree(child, count)
        count = tree_counter_pair[1]
        updated_children.append(tree_counter_pair[0])
    if tree_node.data.label == "":
        return TreeNode(
            NodeData(
                f"{label_counter}",
                tree_node.data.value,
                tree_node.data.tag
            ),
            updated_children
        ), count
    else:
        return TreeNode(
            NodeData(
                tree_node.data.label,
                tree_node.data.value,
                tree_node.data.tag
            ),
            updated_children
        ), count

#TODO: find another way
def add_unique_label(tree_node: TreeNode, new_label: str, i: int = 0) -> str:
    if new_label not in [n.data.label for n in topt.get_all_nodes(tree_node)]:
        return new_label

    # Generate a unique label by appending a number to the original label
    unique_label = str(uuid.uuid1()).replace('-', '')
    return add_unique_label(tree_node, unique_label, i + 1)


def add_node(tree_node: TreeNode, target_node: TreeNode, inserted_node: TreeNode) -> TreeNode:
    if not tree_node.children:
        return TreeNode(NodeData(tree_node.data.label, tree_node.data.value, tree_node.data.tag), [])
    updated_children = []
    new_parent = None
    for child_node in tree_node.children:
        if child_node != target_node:
            updated_child= add_node(child_node, target_node, inserted_node)
            updated_children.append(updated_child)
        else:
            new_parent_label = topt.add_unique_label(tree_node)
            left_child = child_node
            right_child = inserted_node
            new = TreeNode(
                NodeData(
                    new_parent_label,
                    0.0,
                    NodeTag.INSERTED
                ), [left_child, right_child]
            )
            new_parent = new
            updated_children.append(new)
    updated_tree = TreeNode(
        NodeData(
            tree_node.data.label,
            tree_node.data.value,
            tree_node.data.tag),
        updated_children
    )
    return updated_tree


"""def add_node_direct(tree_node: TreeNode, target_node: TreeNode, inserted_node: TreeNode) -> TreeNode:
    if not tree_node.children:
        return TreeNode(NodeData(tree_node.data.label, tree_node.data.value, tree_node.data.tag), [])

    elif tree_node == target_node:
        updated_children = []
        for child in tree_node.children:
            updated_children.append(add_node_direct(child, target_node, inserted_node))
        updated_tree = TreeNode(
            NodeData(
                tree_node.data.label,
                tree_node.data.value,
                tree_node.data.tag),
            updated_children + [inserted_node]
        )
    else:
        updated_children = []
        for child in tree_node.children:
            updated_children.append(add_node_direct(child, target_node, inserted_node))
        updated_tree = TreeNode(
            NodeData(
                tree_node.data.label,
                tree_node.data.value,
                tree_node.data.tag),
            updated_children + [inserted_node]
        )
        return updated_tree"""


def get_parent(tree_node: TreeNode, target: TreeNode, parent: TreeNode) -> TreeNode:
    if tree_node == target:
        return parent
    else:
        result = None
        for child in tree_node.children:
            if not result:
                result = get_parent(child, target, tree_node)
        return result


def get_up_edges(tree_node: TreeNode, targets: List[TreeNode]):
    cur_target = targets[len(targets) - 1]
    cur_parent = topt.get_parent(tree_node, cur_target)
    if cur_parent:
        if len(cur_parent.children) > 1 or not topt.get_parent(tree_node, cur_parent):
            return targets
        else:
            return get_up_edges(tree_node, [cur_parent]) + targets
    else:
        return targets
