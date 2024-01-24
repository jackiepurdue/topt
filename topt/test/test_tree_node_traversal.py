import pytest
import topt.topt as topt
from topt.topt import TreeNode, NodeData


@pytest.fixture
def nested_tree_node():
    leaf_a = topt.create_leaf_tree_node("a")
    leaf_b = topt.create_leaf_tree_node("b")
    leaf_c = topt.create_leaf_tree_node("c")
    leaf_d = topt.create_leaf_tree_node("d")
    primary_e = topt.create_primary_tree_node("0", [leaf_a, leaf_b])
    primary_f = topt.create_primary_tree_node("1", [leaf_c, leaf_d])
    root_r = topt.create_root_tree_node("r", [primary_e, primary_f])
    return root_r


def test_find_parent_with_child_label_exists(nested_tree_node):
    result = topt.find_parent_with_child_label(nested_tree_node, "a")
    assert result.data.label == "0"


def test_find_parent_with_child_label_does_not_exist(nested_tree_node):
    result = topt.find_parent_with_child_label(nested_tree_node, "x")
    assert result is None


def test_find_parent_with_child_label_root(nested_tree_node):
    result = topt.find_parent_with_child_label(nested_tree_node, "r")
    assert result is None


def test_get_leaf_nodes(nested_tree_node):
    assert set([node.data.label for node in topt.get_leaf_nodes(nested_tree_node)]) == {"a", "b", "c", "d"}
    assert set([node.data.label for node in topt.get_leaf_nodes(nested_tree_node)]) != {}
    assert set([node.data.label for node in topt.get_leaf_nodes(nested_tree_node)]) != {"x"}


def test_get_leaf_nodes_single():
    single_node = topt.create_leaf_tree_node("a")
    assert set([node.data.label for node in topt.get_leaf_nodes(single_node)]) == {"a"}
    assert set([node.data.label for node in topt.get_leaf_nodes(single_node)]) != {}
    assert set([node.data.label for node in topt.get_leaf_nodes(single_node)]) != {"x"}


def test_get_leaf_nodes_not_there():
    single_node = None
    assert set([node.data.label for node in topt.get_leaf_nodes(single_node)]) == set()
    assert set([node.data.label for node in topt.get_leaf_nodes(single_node)]) != {"x"}


def test_get_all_nodes():
    tree = TreeNode(
        NodeData("A"),
        [
            TreeNode(
                NodeData("B"),
                [
                    TreeNode(NodeData("C")),
                    TreeNode(NodeData("D")),
                ]
            ),
            TreeNode(NodeData("E")),
            TreeNode(
                NodeData("F"),
                [
                    TreeNode(NodeData("G")),
                    TreeNode(
                        NodeData("H"),
                        [
                            TreeNode(NodeData("I")),
                            TreeNode(NodeData("J")),
                        ]
                    ),
                ]
            ),
        ]
    )

    # Call the function being tested
    result = topt.get_all_nodes(tree)

    # Define the expected output
    expected = [
        TreeNode(NodeData("A")),
        TreeNode(NodeData("B")),
        TreeNode(NodeData("C")),
        TreeNode(NodeData("D")),
        TreeNode(NodeData("E")),
        TreeNode(NodeData("F")),
        TreeNode(NodeData("G")),
        TreeNode(NodeData("H")),
        TreeNode(NodeData("I")),
        TreeNode(NodeData("J")),
    ]

    # Assert that the actual output matches the expected output
    assert {node.data.label for node in topt.get_all_nodes(tree)} == {node.data.label for node in expected}


def test_label_tree_has_all_unique_labels():
    tree_newick = "(((a,b),(c,d)),(e,f));"
    tree = topt.generate_tree_node_from_newick(tree_newick)
    labeled_tree = topt.label_tree(tree, 0)
    all_tree_nodes = [n.data.label for n in topt.get_all_nodes(labeled_tree)]
    assert len(all_tree_nodes) == len(set(all_tree_nodes))


def test_label_tree_has_all_labeled():
    tree_newick = "(((a,b),(c,d)),(e,f));"
    tree = topt.generate_tree_node_from_newick(tree_newick)
    labeled_tree = topt.label_tree(tree, 0)
    num_leaves = len(topt.get_leaf_nodes(labeled_tree))
    all_tree_nodes = [n.data.label for n in topt.get_all_nodes(labeled_tree)]
    assert len(all_tree_nodes) == 2 * num_leaves - 1


@pytest.fixture
def tree() -> TreeNode:
    t = topt.generate_tree_node_from_newick("(A,((B,C),D));")
    return t


def test_find_first_node_by_label(tree):
    # Set up a tree structure for testing

    # Test finding a node with a label that exists
    node = topt.find_first_node_by_label(tree, "B")
    assert node is not None
    assert node.data.label == "B"

    # Test finding a node with a label that doesn't exist
    node = topt.find_first_node_by_label(tree, "Z")
    assert node is None


def test_find_common_ancestor_single_target(tree: TreeNode):
    # Single target label
    target_labels = {"B"}
    expected_ancestor = tree.children[1].children[0].children[0]
    actual_answer = topt.find_common_ancestor(tree, target_labels)
    assert actual_answer == expected_ancestor


def test_find_common_ancestor_different_subtrees(tree: TreeNode):
    # Single target label
    target_labels = {"B", "D"}
    expected_ancestor = tree.children[1]
    actual_answer = topt.find_common_ancestor(tree, target_labels)
    assert actual_answer == expected_ancestor


def test_find_common_ancestor_same_subtree(tree):
    target_labels = {"B", "C"}
    expected_ancestor = tree.children[1].children[0]
    actual_answer = topt.find_common_ancestor(tree, target_labels)
    assert actual_answer == expected_ancestor


def test_find_common_ancestor_not_in_tree(tree):
    # Target label not in the tree
    target_labels = {"E"}
    expected_ancestor = None
    actual_answer = topt.find_common_ancestor(tree, target_labels)
    assert actual_answer == expected_ancestor


def test_find_common_ancestor_one_node_tree(tree):
    # Tree with only one node
    root = topt.create_leaf_tree_node("A")
    target_labels = {"A"}
    expected_ancestor = root
    actual_answer = topt.find_common_ancestor(root, target_labels)
    assert actual_answer == expected_ancestor


def test_find_common_ancestor_one_node_no_match_tree(tree):
    # Tree with only one node but no matching target labels
    root = topt.create_leaf_tree_node("A")
    target_labels = {"B"}
    expected_ancestor = None
    actual_answer = topt.find_common_ancestor(root, target_labels)
    assert actual_answer == expected_ancestor


def test_find_common_ancestor_empty_tree():
    root = None
    target_labels = {"A"}
    expected_ancestor = None
    assert topt.find_common_ancestor(root, target_labels) == expected_ancestor


def test_find_common_ancestor_different_subtrees2_tree():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    print(topt.convert_to_ete(tree2.children[0]))
    print()


def test_find_common_ancestor_different_subtrees3_tree():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    common_ancestor2 = topt.find_common_ancestor(tree2, {"b", "c"})
    assert common_ancestor2 == tree2.children[0]


def test_find_common_ancestor_different_subtrees4_tree():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    common_ancestor2 = topt.find_common_ancestor(tree2, {"b", "c", "f"})
    assert common_ancestor2 == tree2


def test_find_common_ancestor_different_subtrees5_tree():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    common_ancestor2 = topt.find_common_ancestor(tree2, {"b"})
    common_ancestor_find = topt.find_first_node_by_label(tree2, "b")
    assert common_ancestor2 == common_ancestor_find


@pytest.fixture
def tre():
    return topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)


def test_get_parent_root(tre):
    ab = topt.find_common_ancestor(tre, {"a", "b", "c", "d", "f"})
    assert topt.get_parent(tre, ab) == None


def test_get_parent_internal_node(tre):
    ab = topt.find_common_ancestor(tre, {"a", "b"})
    assert topt.get_parent(tre, ab).data.label == "1"


def test_get_parent_leaf_node(tre):
    ab = topt.find_common_ancestor(tre, {"a"})
    assert topt.get_parent(tre, ab).data.label == "2"


def test_get_parent_not_in_tree(tre):
    notin = topt.create_leaf_tree_node("X")
    assert topt.get_parent(tre, notin) == None


def test_get_parent_leaf_node_single_node():
    tree = topt.create_leaf_tree_node("a")
    assert topt.get_parent(tree, tree) == None
