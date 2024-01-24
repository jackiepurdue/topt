import itertools
import uuid
from collections import defaultdict

from topt.topt.data import TreeNode, NodeData, NodeTag, Decision, Status, Record, State, Move
import topt.topt.private.util as _p
import topt.topt as topt
from typing import List, Union, Tuple, Callable, Any, Optional, Set


def find_parent_with_child_label(tree_node: TreeNode, target_label: str) -> TreeNode:
    return _p.find_parent_with_child_label(tree_node, target_label)


def get_leaf_nodes(tree: Union[TreeNode, Decision]) -> List[Union[TreeNode, Decision]]:
    if not tree:
        return []
    elif not tree.children:
        return [tree]
    else:
        return [leaf for child in tree.children for leaf in get_leaf_nodes(child)]


def get_all_nodes(tree: Union[TreeNode, Decision]) -> List[Union[TreeNode, Decision]]:
    if not tree:
        return []
    else:
        nodes = [tree]
        for child in tree.children:
            nodes += get_all_nodes(child)
        return nodes


def generate_newick(tree_node: TreeNode) -> str:
    return f"{_p.generate_newick(tree_node)};"


def delete_node(node: TreeNode, target_node: TreeNode) -> TreeNode:
    updated_children = []
    for child in node.children:
        if child != target_node:
            updated_child = delete_node(child, target_node)
            updated_children.append(updated_child)

    return topt.create_tree_from_node_data(node.data, updated_children)


def delete_node_with_label(node: TreeNode, target_label: str) -> TreeNode:
    updated_children = [delete_node_with_label(child, target_label) for child in node.children if
                        child.data.label != target_label]
    return topt.create_tree_from_node_data(node.data, updated_children)


# TODO: Make more tests for this. Also consider the meaning of branches completley being deleted
def delete_nodes_with_labels(node: TreeNode, target_labels: List[str]) -> TreeNode:
    if not target_labels:
        return node
    return delete_nodes_with_labels(delete_node_with_label(node, target_labels[0]), target_labels[1:])


def prune_node_with_label(node: TreeNode, target_label: str) -> TreeNode:
    if node.children:
        child_labels = [child.data.label for child in node.children]
        if target_label in child_labels and len(child_labels) == 2:
            child_to_keep = [child for child in node.children if target_label != child.data.label]
            if child_to_keep:
                child_to_keep = child_to_keep[0]
                return prune_node_with_label(child_to_keep, target_label)
            else:
                return topt.create_tree_from_node_data(node.data, [])
        else:
            updated_children = [prune_node_with_label(child, target_label) for child in node.children]
            return topt.create_tree_from_node_data(node.data, updated_children)
    else:
        return topt.create_tree_from_node_data(node.data, [])


def prune_nodes_with_labels(node: TreeNode, target_labels: List[str]) -> TreeNode:
    if not target_labels:
        return node
    return prune_nodes_with_labels(prune_node_with_label(node, target_labels[0]), target_labels[1:])


def match_tree_labels(tree_1: TreeNode, tree_2: TreeNode) -> Union[Tuple[TreeNode, TreeNode], None]:
    """
    TODO: Decide what to return when the set of leaf labels in tree_1 does not
    TODO: Think about logging the cases where the second tree is pruned
    """
    leaves_1 = {leaf.data.label for leaf in get_leaf_nodes(tree_1)}
    leaves_2 = {leaf.data.label for leaf in get_leaf_nodes(tree_2)}
    if leaves_1 == leaves_2:
        return prune_nodes_with_labels(tree_1, list()), tree_2
    elif leaves_1.issuperset(leaves_2):
        return prune_nodes_with_labels(tree_1, list(leaves_1 - leaves_2)), tree_2
    elif not leaves_1.intersection(leaves_2):
        return None
    elif not leaves_1.intersection(leaves_2.difference(leaves_1)):
        pruned_tree_2 = prune_nodes_with_labels(tree_2, list(leaves_2.difference(leaves_1)))
        pruned_tree_1 = prune_nodes_with_labels(tree_1, list(
            leaves_1 - set([n.data.label for n in get_leaf_nodes(pruned_tree_2)])))
        return (pruned_tree_1, pruned_tree_2)
    else:
        return None


def match_tree_labels_with_delete(tree_1: TreeNode, tree_2: TreeNode) -> Union[Tuple[TreeNode, TreeNode], None]:
    """
    TODO: Make tests. untested.
    TODO: Decide what to return when the set of leaf labels in tree_1 does not
    TODO: Think about logging the cases where the second tree is pruned
    """
    leaves_1 = {leaf.data.label for leaf in get_leaf_nodes(tree_1)}
    leaves_2 = {leaf.data.label for leaf in get_leaf_nodes(tree_2)}
    if leaves_1 == leaves_2:
        return delete_nodes_with_labels(tree_1, list()), tree_2
    elif leaves_1.issuperset(leaves_2):
        return delete_nodes_with_labels(tree_1, list(leaves_1 - leaves_2)), tree_2
    elif not leaves_1.intersection(leaves_2):
        return None
    elif not leaves_1.intersection(leaves_2.difference(leaves_1)):
        pruned_tree_2 = delete_nodes_with_labels(tree_2, list(leaves_2.difference(leaves_1)))
        pruned_tree_1 = delete_nodes_with_labels(tree_1, list(
            leaves_1 - set([n.data.label for n in get_leaf_nodes(pruned_tree_2)])))
        return (pruned_tree_1, pruned_tree_2)
    else:
        return None


# WARNING: If you change how this works it may break many tests.
# TODO: Fix those tests to accomodate future changes
def label_tree(tree_node: TreeNode, start_number: int) -> TreeNode:
    updated_children = []
    count = start_number
    for child in tree_node.children:
        count = count + 1
        tree_counter_pair = _p.label_tree(child, count)
        count = tree_counter_pair[1]
        updated_children.append(tree_counter_pair[0])
    if tree_node.data.label == "":
        return TreeNode(
            NodeData(
                f"{start_number}",
                tree_node.data.value,
                tree_node.data.tag
            ),
            updated_children
        )
    return _p.label_tree(tree_node, start_number)[0]


def add_node(tree_node: TreeNode, target_node: TreeNode, inserted_node: TreeNode) -> TreeNode:
    if (tree_node == target_node):
        updated_children = []
        for child_node in tree_node.children:
            updated_child = _p.add_node(child_node, target_node, inserted_node)
            updated_children.append(updated_child)

        return TreeNode(
            NodeData(
                add_unique_label(tree_node),
                0.0,
                NodeTag.INSERTED
            ), [tree_node, inserted_node]
        )
    else:
        return _p.add_node(tree_node, target_node, inserted_node)


def add_node_tupled(tree_node: TreeNode, target_node: TreeNode, inserted_node: TreeNode) -> TreeNode:
    if (tree_node == target_node):
        updated_children = []
        for child_node in tree_node.children:
            updated_child = _p.add_node(child_node, target_node, inserted_node)
            updated_children.append(updated_child)

        new_parent = TreeNode(
            NodeData(
                add_unique_label(tree_node),
                0.0,
                NodeTag.INSERTED
            ), [tree_node, inserted_node]
        )
        return new_parent

    else:
        return _p.add_node(tree_node, target_node, inserted_node)


def add_child(tree_node: TreeNode, target_node: TreeNode, inserted_node: TreeNode) -> TreeNode:
    if len(tree_node.children) == 0:
        children = [inserted_node] if (tree_node == target_node) else []
        return TreeNode(
            NodeData(
                tree_node.data.label,
                tree_node.data.value,
                tree_node.data.tag
            ),
            children
        )
    else:
        updated_children = []
        for child_node in tree_node.children:
            updated_child = add_child(child_node, target_node, inserted_node)
            updated_children.append(updated_child)
        updated_children = updated_children + [inserted_node] if (tree_node == target_node) else updated_children
        return TreeNode(
            NodeData(
                tree_node.data.label,
                tree_node.data.value,
                tree_node.data.tag
            ),
            updated_children
        )

#TODO: put this in traversal
def search_node(root: TreeNode, target_label: str) -> Optional[TreeNode]:
    if root is None:
        return None

    if root.data.label == target_label:
        return root

    for child in root.children:
        result = search_node(child, target_label)
        if result is not None:
            return result

    return None

#TODO: need a better way to do this. not efficient.
def add_unique_label(tree_node: TreeNode):
    cur_label = tree_node.data.label
    new_label = cur_label + "-" + str(uuid.uuid1()).replace('-', '')
    #new_new_label = _p.add_unique_label(tree_node, new_label, 0)
    return new_label


def add_outgroup(tree_node: TreeNode, node_to_add: TreeNode) -> TreeNode:
    return TreeNode(
        data=NodeData(
            label="ROOT",
            value=0.0,
            tag=NodeTag.ROOT
        ),
        children=[tree_node, topt.create_leaf_tree_node("X")]
    )


# must be a labeled tree to work (could make an unlabeled version too)
def subtree_delete_and_regraft_tupled(
        tree: TreeNode,
        source_node_to_graft: TreeNode,
        target_graft_location: TreeNode
) -> Tuple[TreeNode, Optional[TreeNode]]:
    tree_with_deleted_element = delete_node(tree, source_node_to_graft)
    tree_with_grafted_element = add_node_tupled(tree_with_deleted_element, target_graft_location, source_node_to_graft)
    source_parent = get_parent(tree, source_node_to_graft)
    return tree_with_grafted_element, source_parent


def subtree_delete_and_regraft_single_labeled_move_tupled(
        tree: TreeNode,
        move: Move
) -> Tuple[TreeNode, Optional[TreeNode]]:
    lca_source = find_common_ancestor(tree, move.source)
    lca_target = find_common_ancestor(tree, move.target)
    return subtree_delete_and_regraft_tupled(tree, lca_source, lca_target)


# must be a labeled tree to work (could make an unlabeled version too)
def reverse_subtree_delete_and_regraft(
        tree: TreeNode,
        source__old_target_parent_node_in_new_tree: TreeNode,
        target__old_source_node_in_new_tree: TreeNode
) -> TreeNode:
    new_tree_rev = topt.delete_node(tree, target__old_source_node_in_new_tree)
    new_tree_rev = topt.add_child(new_tree_rev, source__old_target_parent_node_in_new_tree,
                                  target__old_source_node_in_new_tree)
    # tree_with_grafted_element = add_child(tree, source_to_ungraft, old_parent_target)
    # tree_with_deleted_element = delete_node(tree, source_to_ungraft)

    return new_tree_rev


def reverse_subtree_ungraft_and_regraft_single_labeled_move(
        tree: TreeNode,
        move: Move
) -> TreeNode:
    source__old_source_node_in_new_tree = topt.find_common_ancestor(tree, move.target)
    target__old_source_node_in_new_tree = topt.find_common_ancestor(tree, move.source)

    return reverse_subtree_delete_and_regraft(tree, source__old_source_node_in_new_tree,
                                              target__old_source_node_in_new_tree)


def find_common_ancestor(root: TreeNode, target_labels: Set[str]) -> TreeNode:
    # Figure out how to generalize this (right now it can only handle max 3 child nodes in a tree)
    if root is None or not isinstance(target_labels, set) or root.data.label in target_labels:
        return root
    elif len(target_labels) == 1:
        label = next(iter(target_labels))
        return find_first_node_by_label(root, label)

    p = None
    q = None
    r = None

    if len(root.children) > 0:
        p = find_common_ancestor(root.children[0], target_labels)
    if len(root.children) > 1:
        q = find_common_ancestor(root.children[1], target_labels)
    if len(root.children) > 2:
        r = find_common_ancestor(root.children[2], target_labels)

    if p and q and r:
        return root
    elif p and q:
        return root
    elif p and r:
        return root
    elif q and r:
        return root
    else:
        return p if p else q if q else r


def find_first_node_by_label(root: TreeNode, target_label: str) -> TreeNode:
    if root is None:
        return None

    if root.data.label == target_label:
        return root

    for child in root.children:
        node = find_first_node_by_label(child, target_label)
        if node:
            return node

    return None


#def is_agreement_forest()

# will only work on a labeled tree
def get_node_label_move(tree_node: TreeNode, move: Move):
    source_node_label = find_common_ancestor(tree_node, move.source).data.label
    target_node_label = find_common_ancestor(tree_node, move.target).data.label
    return Move({source_node_label}, {target_node_label})


def get_possible_moves_from_move(tree_node: TreeNode, move: Move) -> List[Move]:
    s = find_common_ancestor(tree_node, move.source)
    t = find_common_ancestor(tree_node, move.target)
    prmv = list(itertools.product(get_up_edges(tree_node, s), get_up_edges(tree_node, t)))
    allmoves = [Move({n[0].data.label}, {n[1].data.label}) for n in prmv]
    return allmoves


def get_parent(tree_node: TreeNode, target: TreeNode):
    return _p.get_parent(tree_node, target, None)


def get_up_edges(tree_node: TreeNode, target: TreeNode):
    return _p.get_up_edges(tree_node, [target])


def get_all_edges_as_tuples(node: Union[TreeNode, Decision], e: List[Tuple[str, str]]):
    if len(node.children) == 0:
        return
    for child in node.children:
        if isinstance(node, TreeNode):
            e.append((node.data.label, child.data.label))
        elif isinstance(node, Decision):
            e.append((node.label, child.label))
        get_all_edges_as_tuples(child, e)


# Temporary and untested. just to fill out the tree quick and dirty
def complete_tree(node: TreeNode, id: int) -> Tuple[TreeNode, int]:
    if node is None or len(node.children) == 0:
        return node, id

    children = []
    new_id = id
    for child in node.children:
        c, i = complete_tree(child, new_id)
        new_id = new_id + i
        children.append(c)
    if len(children) == 1 and node.data.tag != NodeTag.INSERTED: ## Important for visualization these degree 2 nodes will be the targets
        child = node.children[0]
        new_child = TreeNode(NodeData(f"x{new_id}"), [])
        children.append(new_child)
        new_id += 1
    return TreeNode(
        data=NodeData(
            label=node.data.label,
            value=node.data.value,
            tag=node.data.tag
        ),
        children=children
    ), new_id


"""

def get_up_edges(tree_node: TreeNode, leaves: Set[str]):
    lis = []  # TODO: make sure this is the best way to andle no parent (ie top of tree)
    parent = get_parent(tree_node, find_common_ancestor(tree_node, leaves))
    if parent:
        lis = _get_upedges(tree_node, [parent])
        lis = lis + [find_common_ancestor(tree_node, leaves)]
    return _list_to_edge_tuples(lis)


def _list_to_edge_tuples(itms):
    newitms = []
    i = 0
    while i < len(itms) - 1:
        newitms = newitms + [(itms[i], itms[i + 1])]
        i = i + 1
    return newitms


# TODO: make this better
def _get_upedges(tree_node: TreeNode, parent: List[TreeNode]):
    if get_parent(tree_node, parent[len(parent) - 1]):
        if parent[len(parent) - 1].children and len(parent[len(parent) - 1].children) > 1:
            return parent
        elif parent[len(parent) - 1].children and len(parent[len(parent) - 1].children) == 1:
            return _get_upedges(tree_node, [get_parent(tree_node, parent[len(parent) - 1])]) + parent
    else:
        return parent
"""
