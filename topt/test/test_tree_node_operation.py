from typing import Set

import pytest
from ete3 import Tree

import topt.topt as topt
from topt.topt import TreeNode, NodeData, NodeTag, Move


@pytest.fixture
def nested_tree_small():
    leaf_a = topt.create_leaf_tree_node("a")
    leaf_b = topt.create_leaf_tree_node("b")
    primary_i = topt.create_primary_tree_node("0", [leaf_a, leaf_b])
    primary_r = topt.create_primary_tree_node("r", [primary_i])
    return primary_r


@pytest.fixture
def nested_tree_large():
    leaf_a = topt.create_leaf_tree_node("a")
    leaf_b = topt.create_leaf_tree_node("b")
    leaf_c = topt.create_leaf_tree_node("c")
    leaf_d = topt.create_leaf_tree_node("d")
    leaf_e = topt.create_leaf_tree_node("e")
    leaf_f = topt.create_leaf_tree_node("f")
    primary_0 = topt.create_primary_tree_node("0", [leaf_a, leaf_b])
    primary_1 = topt.create_primary_tree_node("1", [leaf_c, primary_0])
    primary_2 = topt.create_primary_tree_node("2", [leaf_d, leaf_e])
    primary_3 = topt.create_primary_tree_node("3", [primary_1, primary_2])
    primary_r = topt.create_primary_tree_node("r", [primary_3, leaf_f])
    return primary_r


def test_delete_node_with_label_at(nested_tree_small):
    print(topt.convert_to_ete(nested_tree_small))
    new_root = topt.delete_node_with_label(nested_tree_small, "b")

    print(topt.convert_to_ete(new_root))
    assert len(new_root.children) == 1
    assert len(new_root.children[0].children) == 1
    assert len(nested_tree_small.children[0].children) == 2
    assert {node.data.label for node in topt.get_leaf_nodes(nested_tree_small)} == {"a", "b"}
    assert {node.data.label for node in topt.get_leaf_nodes(new_root)} == {"a"}


def test_delete_node_at(nested_tree_small):
    print(topt.convert_to_ete(nested_tree_small))
    new_root = topt.delete_node(nested_tree_small, nested_tree_small.children[0].children[1])
    print(topt.convert_to_ete(new_root))
    assert len(new_root.children) == 1
    assert len(new_root.children[0].children) == 1
    assert len(nested_tree_small.children[0].children) == 2
    assert {node.data.label for node in topt.get_leaf_nodes(nested_tree_small)} == {"a", "b"}
    assert {node.data.label for node in topt.get_leaf_nodes(new_root)} == {"a"}


def test_delete_node_with_label_inner(nested_tree_small):
    new_root = topt.delete_node_with_label(nested_tree_small, "0")
    assert new_root.children == []


def test_delete_node_inner(nested_tree_small):
    new_root = topt.delete_node(nested_tree_small, nested_tree_small.children[0])
    assert new_root.children == []


def test_delete_node_with_label_non_existant(nested_tree_small):
    new_root = topt.delete_node_with_label(nested_tree_small, "x")
    assert new_root == nested_tree_small

    new_root = topt.delete_node_with_label(nested_tree_small, "r")
    assert new_root == nested_tree_small


def test_delete_node_non_existant(nested_tree_small):
    new_root = topt.delete_node_with_label(nested_tree_small, topt.create_leaf_tree_node("x"))
    assert new_root == nested_tree_small
    new_root = topt.delete_node_with_label(nested_tree_small, nested_tree_small)
    assert new_root == nested_tree_small


def test_delete_nodes_with_labels_at_d_and_c(nested_tree_large):
    pruned_root = topt.delete_nodes_with_labels(nested_tree_large, ["d", "c"])
    assert any(n not in topt.generate_newick(pruned_root) for n in ["d", "c"])
    parent_of_deleted_d = topt.find_parent_with_child_label(pruned_root, "e")
    assert parent_of_deleted_d is not None
    assert len(parent_of_deleted_d.children) == 1
    parent_of_deleted_c = topt.find_parent_with_child_label(pruned_root, "0")
    assert parent_of_deleted_c is not None
    assert len(parent_of_deleted_c.children) == 1
    assert any(n in topt.generate_newick(pruned_root) for n in ["a", "b", "e", "f", "0", "1", "2", "3", "r"])


def test_prune_node_at_e(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "e")
    assert topt.generate_newick(pruned_root) == "(((c,(a,b)0)1,d)3,f)r;"


def test_prune_node_at_b(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "b")
    assert topt.generate_newick(pruned_root) == "(((c,a)1,(d,e)2)3,f)r;"


def test_prune_node_at_d(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "d")
    assert topt.generate_newick(pruned_root) == "(((c,(a,b)0)1,e)3,f)r;"


def test_prune_node_at_f(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "f")
    assert topt.generate_newick(pruned_root) == "((c,(a,b)0)1,(d,e)2)3;"


def test_prune_node_at_0(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "0")
    assert topt.generate_newick(pruned_root) == "((c,(d,e)2)3,f)r;"


def test_prune_node_at_3(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "3")
    assert topt.generate_newick(pruned_root) == "f;"


def test_prune_node_at_r(nested_tree_large):
    pruned_root = topt.prune_node_with_label(nested_tree_large, "r")
    assert topt.generate_newick(pruned_root) == "(((c,(a,b)0)1,(d,e)2)3,f)r;"


def test_prune_node_at_a_and_b(nested_tree_large):
    pruned_root = topt.prune_nodes_with_labels(nested_tree_large, ["a", "b"])
    assert topt.generate_newick(pruned_root) == "((c,(d,e)2)3,f)r;"


def test_prune_node_at_d_and_c(nested_tree_large):
    pruned_root = topt.prune_nodes_with_labels(nested_tree_large, ["d", "c"])
    assert topt.generate_newick(pruned_root) == "(((a,b)0,e)3,f)r;"


def test_match_tree_labels():
    tree_1_newick = "((((a,f),((b,g),e)),(c,h)),(d,i));"
    tree_2_newick = "(((d,(a,e)),c),f);"
    tree_1 = topt.generate_tree_node_from_newick(tree_1_newick)
    tree_2 = topt.generate_tree_node_from_newick(tree_2_newick)

    pruned_tree_1 = topt.match_tree_labels(tree_1, tree_2)
    tree_1_pruned_labels = set([node.data.label for node in topt.get_leaf_nodes(pruned_tree_1[0])])
    tree_2_labels = set([node.data.label for node in topt.get_leaf_nodes(tree_2)])

    assert tree_1_pruned_labels == tree_2_labels


def test_match_tree_labels_reversed_order():
    tree_1_newick = "(((d,(a,e)),c),f);"
    tree_2_newick = "((((a,f),((b,g),e)),(c,h)),(d,i));"
    tree_1 = topt.generate_tree_node_from_newick(tree_1_newick)
    tree_2 = topt.generate_tree_node_from_newick(tree_2_newick)
    pruned_trees = topt.match_tree_labels(tree_1, tree_2)
    pruned_tree_1 = pruned_trees[0]
    pruned_tree_2 = pruned_trees[1]
    tree_1_pruned_labels = set([node.data.label for node in topt.get_leaf_nodes(pruned_tree_1)])
    tree_2_pruned_labels = set([node.data.label for node in topt.get_leaf_nodes(pruned_tree_2)])
    assert tree_1_pruned_labels == tree_2_pruned_labels


def test_match_tree_labels_identical_trees():
    tree_1_newick = "(((a,b),(c,d)),(e,f));"
    tree_2_newick = "(((a,b),(c,d)),(e,f));"
    tree_1 = topt.generate_tree_node_from_newick(tree_1_newick)
    tree_2 = topt.generate_tree_node_from_newick(tree_2_newick)

    pruned_tree_1 = topt.match_tree_labels(tree_1, tree_2)
    tree_1_pruned_labels = set([node.data.label for node in topt.get_leaf_nodes(pruned_tree_1[0])])
    tree_2_labels = set([node.data.label for node in topt.get_leaf_nodes(tree_2)])

    assert tree_1_pruned_labels == tree_2_labels


def test_match_tree_labels_disjoint_trees():
    tree_1_newick = "(((a,b),(c,d)),(e,f));"
    tree_2_newick = "(((g,h),(i,j)),(k,l));"
    tree_1 = topt.generate_tree_node_from_newick(tree_1_newick)
    tree_2 = topt.generate_tree_node_from_newick(tree_2_newick)

    pruned_tree_1 = topt.match_tree_labels(tree_1, tree_2)
    assert pruned_tree_1 is None


@pytest.fixture
def example_tree():
    # Example tree structure for testing
    return TreeNode(NodeData('A', 1), [
        TreeNode(NodeData('B', 2), [
            TreeNode(NodeData('D', 4), []),
            TreeNode(NodeData('E', 5), []),
        ]),
        TreeNode(NodeData('C', 3), [
            TreeNode(NodeData('F', 6), []),
            TreeNode(NodeData('G', 7), []),
        ])
    ])


def test_add_node_to_leaf(example_tree):
    # Test adding a node to a leaf node
    print(topt.convert_to_ete(example_tree))
    new_node = TreeNode(NodeData('H', 8), [])
    updated_tree = topt.add_node(example_tree, example_tree.children[1].children[1], new_node)
    print(topt.convert_to_ete(updated_tree))
    print(topt.generate_newick(updated_tree))
    assert {n.data.label for n in updated_tree.children[1].children[1].children} == {"G", "H"}
    assert updated_tree.children[1].children[1].data.tag == NodeTag.INSERTED


# TODO: Make actual assertions (visual test for now)
def test_add_child(example_tree):
    print(topt.convert_to_ete(example_tree))
    new_node = TreeNode(NodeData('H', 8), [])
    updated_tree = topt.add_child(example_tree, example_tree.children[1].children[1], new_node)
    print(topt.convert_to_ete(updated_tree))
    print(topt.generate_newick(updated_tree))

    new_node2 = TreeNode(NodeData('I', 8), [])
    updated_tree2 = topt.add_child(updated_tree, updated_tree.children[1].children[1], new_node2)
    print(topt.convert_to_ete(updated_tree2))
    print(topt.generate_newick(updated_tree2))

    new_node3 = TreeNode(NodeData('J', 8), [])
    updated_tree3 = topt.add_child(updated_tree2, updated_tree2.children[1], new_node3)
    print(topt.convert_to_ete(updated_tree3))
    print(topt.generate_newick(updated_tree3))

    updated_tree4 = topt.delete_node(updated_tree3, updated_tree3.children[1].children[0])
    print(topt.convert_to_ete(updated_tree4))
    print(topt.generate_newick(updated_tree4))

    new_node_k = TreeNode(NodeData('K', 8), [])
    updated_tree5 = topt.add_child(updated_tree4, updated_tree4, new_node_k)
    print(topt.convert_to_ete(updated_tree5))
    print(topt.generate_newick(updated_tree5))

    updated_tree6 = topt.delete_node(updated_tree5, updated_tree5.children[0])
    print(topt.convert_to_ete(updated_tree6))
    print(topt.generate_newick(updated_tree6))

    new_node_l = TreeNode(NodeData('L', 8), [])
    updated_tree7 = topt.add_child(updated_tree6, updated_tree6.children[0].children[0].children[1], new_node_l)
    print(topt.convert_to_ete(updated_tree7))
    print(topt.generate_newick(updated_tree7))
    # assert {n.data.label for n in updated_tree.children[1].children[1].children} == {"G", "H"}
    # assert updated_tree.children[1].children[1].data.tag == NodeTag.INSERTED


def test_add_node_to_nonleaf(example_tree):
    # Test adding a node to a non-leaf node
    print(topt.convert_to_ete(example_tree))
    new_node = TreeNode(NodeData('H', 8), [])
    updated_tree = topt.add_node(example_tree, example_tree.children[1], new_node)
    print(topt.convert_to_ete(updated_tree))
    assert {n.data.label for n in updated_tree.children[1].children} == {"H", "C"}
    assert updated_tree.children[1].data.tag == NodeTag.INSERTED


def test_add_node_to_root(example_tree):
    # Test adding a node to the root node
    print(topt.convert_to_ete(example_tree))
    new_node = TreeNode(NodeData('H', 8), [])
    updated_tree = topt.add_node(example_tree, example_tree, new_node)
    print(topt.convert_to_ete(updated_tree))
    assert updated_tree.data.tag == NodeTag.INSERTED


def test_add_outgroup(example_tree):
    # Test adding a node to the root node
    print(topt.convert_to_ete(example_tree))
    new_node = TreeNode(NodeData('H', 8), [])
    updated_tree = topt.add_outgroup(example_tree, new_node)
    print(topt.convert_to_ete(updated_tree))


def test_add_node_to_nonexistent_sibling(example_tree):
    # Test adding a node to a nonexistent sibling node
    new_node = TreeNode(NodeData('H', 8), [])
    updated_tree = topt.add_node(example_tree, TreeNode(NodeData('nonexist', 9), []), new_node)
    assert topt.generate_newick(updated_tree) == topt.generate_newick(example_tree)


# TODO: Test uniquness of labels from adds
# TODO: These tests are jsut visual at the moment. fix that
# TODO: Notice the 2 types of SDR operations
# TODO: Refactor

def test_subtree_delete_and_regraft_tupled():
    tree2 = topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);")
    node_to_graft = topt.find_first_node_by_label(tree2, "C")
    graft_location = topt.find_first_node_by_label(tree2, "B")

    new_tree, parent_node = topt.subtree_delete_and_regraft_tupled(tree2, node_to_graft, graft_location)
    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    print(topt.convert_to_ete(parent_node))
    expected_new_tree = topt.generate_tree_node_from_newick("(A,B,(C,E,D));")


def test_subtree_delete_and_regraft_tupled_move():
    tree2 = topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);")
    move = Move({"C"}, {"B"})
    new_tree, parent_node = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree2, move)
    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    print(topt.convert_to_ete(parent_node))
    expected_new_tree = topt.generate_tree_node_from_newick("(A,B,(C,E,D));")


def test_subtree_delete_and_regraft_tupled_2():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);"), 0)
    node_to_graft = topt.find_common_ancestor(tree2, {"C", "D"})
    graft_location = topt.find_common_ancestor(tree2, {"E"})

    new_tree, parent_node = topt.subtree_delete_and_regraft_tupled(tree2, node_to_graft, graft_location)
    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    # print(topt.convert_to_ete(parent_node))
    expected_new_tree = topt.generate_tree_node_from_newick("(A,B,(C,E,D));")


def test_subtree_delete_and_regraft_tupled_2_move():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);"), 0)
    node_to_graft = topt.find_common_ancestor(tree2, {"C", "D"})
    graft_location = topt.find_common_ancestor(tree2, {"E"})
    move = Move({"C", "D"}, {"E"})
    new_tree, parent_node = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree2, move)
    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    print(parent_node.data.label)
    # print(topt.convert_to_ete(parent_node))
    expected_new_tree = topt.generate_tree_node_from_newick("(A,B,(C,E,D));")


def test_subtree_delete_and_regraft_tupled_3():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    node_to_graft = topt.find_common_ancestor(tree2, {"c", "d"})
    graft_location = topt.find_common_ancestor(tree2, {"e", "f"})

    new_tree, parent_node = topt.subtree_delete_and_regraft_tupled(tree2, node_to_graft, graft_location)

    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    print(topt.convert_to_ete(parent_node))
    node_to_graft2 = topt.find_common_ancestor(new_tree, {"b"})
    graft_location2 = topt.find_common_ancestor(new_tree, {"c", "d"})

    print("------")
    new_tree2, parent_node2 = topt.subtree_delete_and_regraft_tupled(new_tree, node_to_graft2, graft_location2)
    print(topt.convert_to_ete(new_tree))
    print(topt.convert_to_ete(new_tree2))
    print(topt.convert_to_ete(parent_node2))

    # print(topt.convert_to_ete(parent_node))


def test_subtree_delete_and_regraft_tupled_4():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    node_to_graft = topt.find_common_ancestor(tree2, {"a"})
    graft_location = topt.find_common_ancestor(tree2, {"a", "b"})

    new_tree, parent_node = topt.subtree_delete_and_regraft_tupled(tree2, node_to_graft, graft_location)

    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    print(topt.convert_to_ete(parent_node))
    # print(topt.convert_to_ete(parent_node))


# failing
def test_subtree_delete_and_regraft_tupled_5():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    node_to_graft = topt.find_common_ancestor(tree2, {"a"})
    graft_location = topt.find_common_ancestor(tree2, {"a", "b", "c", "d"})

    new_tree, parent_node = topt.subtree_delete_and_regraft_tupled(tree2, node_to_graft, graft_location)

    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    # print(topt.convert_to_ete(parent_node))


def test_subtree_delete_and_regraft_tupled_5():
    tree2 = topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));")
    node_to_graft = topt.find_common_ancestor(tree2, {"a"})
    graft_location = tree2

    new_tree, parent_node = topt.subtree_delete_and_regraft_tupled(tree2, node_to_graft, graft_location)

    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))


def test_subtree_delete_and_regraft_tupled_move_at_node_instead_of_leaf_ancestor():
    tree2 = topt.label_tree(topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);"), 0)
    move = Move({"5"}, {"B"})  # CD to B
    new_tree, parent_node = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree2, move)
    print(topt.convert_to_ete(tree2))
    print(topt.convert_to_ete(new_tree))
    print(topt.convert_to_ete(parent_node))


def test_reverse_subtree_delete_and_regraft_tupled_move_at_node_instead_of_leaf_ancestor():
    original_tree = topt.label_tree(topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);"), 0)
    original_source_node_label = "5"  # CD to B
    original_target_node_label = "B"
    move = Move({original_source_node_label}, {original_target_node_label})  # CD to B
    modified_tree, original_source_parent = topt.subtree_delete_and_regraft_single_labeled_move_tupled(original_tree,
                                                                                                       move)
    print(topt.convert_to_ete(original_tree))
    print(topt.convert_to_ete(modified_tree))
    print(topt.convert_to_ete(original_source_parent))
    print("===")
    # reversed_move = Move({"5"}, {"3"})
    # new_tree_rev= topt.reverse_subtree_ungraft_and_regraft_single_labeled_move(new_tree, reversed_move)
    source__old_source_parent_node_in_new_tree = topt.find_common_ancestor(modified_tree,
                                                                           {original_source_parent.data.label})
    target__old_source_node_in_new_tree = topt.find_common_ancestor(modified_tree, {original_source_node_label})

    # new_tree_rev = topt.delete_node(modified_tree, target__old_source_node_in_new_tree)
    # new_tree_rev = topt.add_child(new_tree_rev, source__old_source_parent_node_in_new_tree, target__old_source_node_in_new_tree)
    #
    reverse_move = Move({original_source_parent.data.label}, {original_source_node_label})
    new_tree_rev = topt.reverse_subtree_ungraft_and_regraft_single_labeled_move(modified_tree, reverse_move)
    print(topt.convert_to_ete(modified_tree))
    print(topt.convert_to_ete(new_tree_rev))
    # print(topt.convert_to_ete(parent_node))


def test_reverse_subtree_delete_and_regraft_tupled_move_sequence():
    original_tree = topt.label_tree(topt.generate_tree_node_from_newick("((e,((a,b),(c,d))),f);"), 0)
    print(topt.convert_to_ete(original_tree))
    base_moves = [Move({"c", "d"}, {"f"}),Move({"d"}, {"f"}), Move({"a"}, {"f", "d"})]
    applied_moves = []
    reverse_moves = []

    tree = original_tree
    for base_move in base_moves:
        tree, last_source_parent = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree, base_move)
        actual_applied = Move(
            {topt.find_common_ancestor(original_tree, base_move.source).data.label},
            {topt.find_common_ancestor(original_tree, base_move.target).data.label}
        )
        applied_moves.append(actual_applied)
        cd_f_reverse_move = Move(actual_applied.source, {last_source_parent.data.label})
        reverse_moves.append(cd_f_reverse_move)
        print(base_move)
        print(topt.convert_to_ete(tree))

#then start reversing
    reverse_moves.reverse()
    for reverse_move in reverse_moves:
        tree = topt.reverse_subtree_ungraft_and_regraft_single_labeled_move(tree, reverse_move)
        print(reverse_move)
        print(topt.convert_to_ete(tree))
