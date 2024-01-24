from functools import partial
from typing import Optional, Tuple

import pytest

import topt.topt as topt
from topt.topt import TreeNode, Move, NodeData, Record, Status


"""def match_isomorphic_tree_labels(reference_tree: TreeNode, node: TreeNode) -> Optional[TreeNode]:
    if reference_tree is None or node is None:
        return None

    # check if the labels match
    if reference_tree.data.label != node.data.label:
        
        children = []
        
        for child in reference_tree:
            match_isomorphic_tree_labels(child, node.children[i])
        
        TreeNode(
            data=NodeData(
                label=node.data.label,
                value=node.data.value,
                tag=node.data.tag
            ),
            children=[left_subtree, right_subtree])

    # if both nodes are leaves, we've found a match
    if not reference_tree.children and not node.children:
        return reference_tree

    # if one is a leaf and the other is not, they can't be isomorphic
    if (not reference_tree.children and node.children) or (reference_tree.children and not node.children):
        return None

    # compare the subtrees recursively
    for i in range(len(reference_tree.children)):
        match = match_isomorphic_tree_labels(reference_tree.children[i], node.children[i])
        if match is not None:
            return match

    # if we haven't returned yet, there was no match
    return None
"""


def complete_tree(node: TreeNode, id: int) -> Tuple[TreeNode, int]:
    if node is None or len(node.children) == 0:
        return node, id

    children = []
    new_id = id
    for child in node.children:
        c, i = complete_tree(child, new_id)
        new_id = new_id + i
        children.append(c)
    if len(children) == 1:
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


def test_matchlabeling_of_final_product():
    """    Record(topt.generate_tree_node_from_newick(("((a,b),((c,(d,e)),(f,g)));"))),
        Record(topt.generate_tree_node_from_newick("(a,(b,((((c,d),e),f),g)));"))]
        data_record = [
        Record(topt.generate_tree_node_from_newick(("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))),
    Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    '((((a,b),(c,d)),(e,f)),(g,(h,i)));'), ('(a,((b,c),(((d,e),f),((g,h),i))));'"""
    data_record = [
        Record(topt.generate_tree_node_from_newick(
            ("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_compare_get_moves_decision,
            topt.make_multiple_move_expander_decision,
            topt.make_reverse_spd_moves_decision,
            topt.make_all_edge_decision
        ]
    )

    reference_tree = topt.generate_tree_node_from_newick(
        ("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))
    final_decisions = [d for d in topt.get_all_nodes(decision) if not d.children]
    
    first_choice = final_decisions[0].data[0].node
    #match_isomorphic_tree_labels(reference_tree, final_decisions[0].data[0].node) # for now going to hjust insert x for missing
    print(topt.convert_to_ete(first_choice))
    ct = complete_tree(first_choice, 0)[0]
    print(topt.convert_to_ete(ct))
    #print()
