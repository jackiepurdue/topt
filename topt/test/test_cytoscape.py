import topt.topt as topt
from topt.topt import Record, Status


def test_build_cytoscape_json():
    newick = "(a,((b,c),(((d,e),f),((g,h),i))));"
    labeled_tree = topt.label_tree(topt.generate_tree_node_from_newick(newick), 0)
    json_tree = topt.build_tree_node_json(labeled_tree)
    assert len(json_tree["nodes"]) == len(topt.get_all_nodes(labeled_tree))
    #test matches a template for cytoscape tree

def test_build_decision_json():
    data_record = [
        Record(topt.generate_tree_node_from_newick("((((a,b),(c,d)),(e,f)),(g,(h,i)));")),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_compare_get_moves_decision,
            topt.make_multiple_move_expander_decision,
            topt.make_reverse_spd_moves_decision
        ]
    )

    decison_json = topt.build_decision_json(decision)
    print()

def test_add_spr_edges_json():
    data_record = [
        Record(topt.generate_tree_node_from_newick("((((a,b),(c,d)),(e,f)),(g,(h,i)));")),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_compare_get_moves_decision,
            topt.make_multiple_move_expander_decision,
            topt.make_reverse_spd_moves_decision
        ]
    )

    decison_json = topt.build_decision_json(decision)

    decison_json_with_edges = topt.add_expanding_spr_edges_to_tree_node_json(decision.children[0].children[0].children[0].children[0].children[0].data[0].node
                                                                             , decison_json,
                                                                             decision.children[0].children[0].children[0].children[0].children[0].data[0].moves.possible)
    print()