from functools import partial
from typing import List, Callable

import random as rand

from topt import topt
from topt.topt.data import TreeNode, NodeData, NodeTag, Decision, Record, Status, State

def create_leaf_tree_node(label: str) -> TreeNode:
    return TreeNode(
        NodeData(
            label=label,
            tag=NodeTag.LEAF
        ),
        children=[]
    )


def create_primary_tree_node(label: str, children: List[TreeNode]):
    return TreeNode(
        NodeData(
            label=label,
            tag=NodeTag.PRIMARY
        ),
        children=children
    )


def create_root_tree_node(label: str, children: List[TreeNode]):
    return TreeNode(
        NodeData(
            label=label,
            tag=NodeTag.ROOT
        ),
        children=children
    )


def create_tree_from_node_data(node_data: NodeData, children: List[TreeNode]):
    return TreeNode(
        NodeData(
            label=node_data.label,
            value=node_data.value,
            tag=node_data.tag
        ),
        children=children
    )


def make_start_comparison_decision(
        tree1: TreeNode,
        tree2: TreeNode,
        children: List[Decision] = []
) -> Decision:
    return Decision(
        data=[
            Record(
                tree1,
            ),
            Record(
                tree2,
            ),
        ],
        status=Status(
            state=State.START
        )
    )


def initialize_empty_decision() -> Decision:
    return Decision(
        data=[
            Record(
                TreeNode(),
            ),
        ]
    )


def create_random_binary_tree(min_leaves: int, max_leaves: int, labels: List[str]) -> TreeNode:
    """
    TODO: This list is being emptied because it is mutable. Find another way to do this.
    """
    if min_leaves > max_leaves:
        raise ValueError("Minimum number of leaves cannot be greater than maximum number of leaves.")
    if len(labels) < max_leaves:
        raise ValueError("Minimum number of labels cannot be greater than maximum number of leaves.")
    num_leaves = rand.randint(min_leaves, max_leaves)
    return create_random_binary_tree_helper(num_leaves, labels)


def create_random_binary_tree_helper(num_leaves: int, labels: List[str]) -> TreeNode:
    """
    TODO: Refactor
    TODO: This list is being emptied because it is mutable. Find another way to do this.
    """
    if num_leaves == 1:
        label = labels.pop(0)
        return TreeNode(data=NodeData(tag=NodeTag.LEAF, label=label))
    left_num_leaves = rand.randint(1, num_leaves - 1)
    right_num_leaves = num_leaves - left_num_leaves
    left_subtree = create_random_binary_tree_helper(left_num_leaves, labels)
    right_subtree = create_random_binary_tree_helper(right_num_leaves, labels)

    label = ""  # labels.pop(0)
    return TreeNode(data=NodeData(tag=NodeTag.PRIMARY, label=label), children=[left_subtree, right_subtree])
