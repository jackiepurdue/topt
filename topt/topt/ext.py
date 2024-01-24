import math as math
from typing import List, Tuple, Callable
from ete3 import Tree
from topt.topt.data import TreeNode, Status, Record, State, Decision, MoveGroup
import topt.topt.io as io
import topt.topt.util as util
import topt.topt.factory as factory
import topt.topt.private.ext as _p


def run(trees: List[str]) -> str:
    """
    TODO: Refactor
    """
    if len(trees) >= 2:
        return io.run_with_show_moves(trees)


def create_tree_pairs_with_minimum_spr_distance_with_subset_of_this_reference_tree(
        tree: TreeNode, spr_distance: int,
        number_to_generate: int) -> List[
    Tuple[str, str]]:
    """
    TODO: Refactor
    """
    labels = [n.data.label for n in util.get_leaf_nodes(tree)]
    i = 0
    tree_pairs = []
    while i < number_to_generate:

        random_tree = factory.create_random_binary_tree(math.floor(4), 4, labels.copy())
        newick = util.get_leaf_nodes(tree)
        #print(newick)
        result_str = run([util.generate_newick(tree), util.generate_newick(random_tree)])
        all_moves = _p.parse_ancestor_moves(result_str)
        num_moves = len(all_moves)
        if num_moves >= spr_distance:
            tree_pairs.append((util.generate_newick(tree), util.generate_newick(random_tree)))
            i = i + 1
    return tree_pairs


def generate_tree_node_from_newick(newick: str) -> TreeNode:
    ete_tree = Tree(newick, format=1)
    return convert_to_node(ete_tree)


def convert_to_node(ete_tree: Tree, is_root=True) -> TreeNode:
    children = [convert_to_node(child, False) for child in ete_tree.get_children()]
    if is_root:
        return factory.create_root_tree_node(ete_tree.name, children)
    elif ete_tree.is_leaf():
        return factory.create_leaf_tree_node(ete_tree.name)
    else:
        return factory.create_primary_tree_node(ete_tree.name, children)


def convert_to_ete(tree_node: TreeNode) -> Tree:
    return Tree(util.generate_newick(tree_node), format=1)


