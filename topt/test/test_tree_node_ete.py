import pytest
from ete3 import Tree
import topt.topt as topt


@pytest.fixture
def nested_node_tree():
    leaf_a = topt.create_leaf_tree_node("a")
    leaf_b = topt.create_leaf_tree_node("b")
    leaf_c = topt.create_leaf_tree_node("c")
    leaf_d = topt.create_leaf_tree_node("d")

    primary_0 = topt.create_primary_tree_node("", [leaf_c, leaf_d])
    primary_1 = topt.create_primary_tree_node("", [leaf_b, primary_0])
    root_r = topt.create_root_tree_node("", [leaf_a, primary_1])

    return root_r


@pytest.fixture
def nested_node_tree_newick():
    return "(a,(b,(c,d)));"


def test_generate_tree_node_from_newick(nested_node_tree_newick, nested_node_tree):
    assert topt.generate_tree_node_from_newick(nested_node_tree_newick) == nested_node_tree


def test_convert_to_node(nested_node_tree_newick, nested_node_tree):
    ete_tree = Tree(nested_node_tree_newick)
    assert topt.convert_to_node(ete_tree) == nested_node_tree


def test_generate_newick(nested_node_tree_newick, nested_node_tree):
    assert topt.generate_newick(nested_node_tree) == nested_node_tree_newick


def test_convert_to_ete(nested_node_tree_newick, nested_node_tree):
    expected_ete_tree = Tree(nested_node_tree_newick)
    actual_ete_tree = topt.convert_to_ete(nested_node_tree)
    assert actual_ete_tree.compare(expected_ete_tree)
