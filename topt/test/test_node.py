import json
import pytest

from topt.topt import *

@pytest.fixture
def default_node():
    return TreeNode()


@pytest.fixture
def node_with_different_label():
    return TreeNode(NodeData(label="different"))


@pytest.fixture
def nested_node_tree():
    node_data_root = NodeData(label="r", value=1.0, tag=NodeTag.ROOT)
    node_data_a = NodeData(label="a", value=2.0, tag=NodeTag.PRIMARY)
    node_data_b = NodeData(label="b", value=3.0, tag=NodeTag.LEAF)
    node_data_c = NodeData(label="c", value=3.0, tag=NodeTag.LEAF)
    node_c = TreeNode(node_data_c)
    node_b = TreeNode(node_data_b)
    node_a = TreeNode(node_data_a, [node_b, node_c])
    node_root = TreeNode(node_data_root, [node_a])
    return node_root


def test_default_node(default_node):
    assert default_node.data.label == ""
    assert default_node.data.value == 0.0
    assert default_node.data.tag == NodeTag.DEFAULT
    assert default_node.children == []


def test_node_equivalence(default_node, node_with_different_label):
    assert default_node != node_with_different_label


def test_node_string_representation(nested_node_tree):
    expected_str = "Node(data=NodeData(label=r, value=1.0, tag=root), " \
                   "children=[Node(data=NodeData(label=a, value=2.0, tag=primary), " \
                   "children=[Node(data=NodeData(label=b, value=3.0, tag=leaf), children=[]), " \
                   "Node(data=NodeData(label=c, value=3.0, tag=leaf), children=[])])])"
    assert str(nested_node_tree).replace("'", "") == expected_str


def test_node_serialization(nested_node_tree):
    expected_output = {
        "data": {
            "label": "r",
            "value": 1.0,
            "tag": "root"
        },
        "children": [
            {
                "data": {
                    "label": "a",
                    "value": 2.0,
                    "tag": "primary"
                },
                "children": [
                    {
                        "data": {
                            "label": "b",
                            "value": 3.0,
                            "tag": "leaf"
                        },
                        "children": []
                    },
                    {
                        "data": {
                            "label": "c",
                            "value": 3.0,
                            "tag": "leaf"
                        },
                        "children": []
                    }
                ]
            }
        ]
    }

    actual_output = json.loads(nested_node_tree.to_json())
    assert actual_output == expected_output