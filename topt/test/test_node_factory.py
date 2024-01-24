import pytest

import topt.topt as topt
from topt.topt.data import NodeTag


def test_create_leaf_tree_node():
    node = topt.create_leaf_tree_node("a")
    assert node.data.label == "a"
    assert node.data.tag == NodeTag.LEAF
    assert node.children == []


def test_create_primary_tree_node():
    child1 = topt.create_leaf_tree_node("b")
    child2 = topt.create_leaf_tree_node("c")
    node = topt.create_primary_tree_node("a", [child1, child2])
    assert node.data.label == "a"
    assert node.data.tag == NodeTag.PRIMARY
    assert node.children == [child1, child2]


def test_create_root_tree_node():
    child1 = topt.create_leaf_tree_node("b")
    child2 = topt.create_primary_tree_node("c", [topt.create_leaf_tree_node("d")])
    node = topt.create_root_tree_node("a", [child1, child2])
    assert node.data.label == "a"
    assert node.data.tag == NodeTag.ROOT
    assert node.children == [child1, child2]


def test_create_tree_from_node_data():
    child1 = topt.create_leaf_tree_node("b")
    child2 = topt.create_primary_tree_node("c", [topt.create_leaf_tree_node("d")])
    node_data = topt.NodeData(
        label="a",
        value=1.0,
        tag=NodeTag.INSERTED
    )
    node = topt.create_tree_from_node_data(node_data, [child1, child2])
    assert node.data.label == "a"
    assert node.data.value == 1.0
    assert node.data.tag == NodeTag.INSERTED
    assert node.children == [child1, child2]

