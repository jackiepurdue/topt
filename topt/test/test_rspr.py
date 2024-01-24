import topt.topt as topt
from topt.topt import Record, Status, State, Move


def test_rspr_comparison_basic():
    tree1 = topt.generate_tree_node_from_newick("(((a,b),c),d);")
    tree2 = topt.generate_tree_node_from_newick("((a,(b,c)),d);")
    tree3 = topt.generate_tree_node_from_newick("((a,(b,c)),d);")

    record1 = Record(node=tree1)
    record2 = Record(node=tree2)
    record3 = Record(node=tree2)
    status = Status(state=State.MATCHED)

    decision = topt.make_compare_get_moves_decision([record1, record2, record3], status, [])
    assert decision.status.state == State.COMPARED
    #assert decision.data[0].moves.possible == [Move(source={'c'}, target={'b'})]
    assert decision.data[0].moves.base == []


def test_rspr_comparison_multiple():
    # These have a minimum SPR distance of 4
    tree1 = topt.generate_tree_node_from_newick("(((a,b),c),(d,(e,((f,g),(h,i)))));")
    tree2 = topt.generate_tree_node_from_newick("((a,(b,((c,d),(e,f)))),((g,h),i));")

    record1 = Record(node=tree1)
    record2 = Record(node=tree2)
    record3 = Record(node=tree2)
    status = Status(state=State.MATCHED)

    decision = topt.make_compare_get_moves_decision([record1, record2, record3], status, [])
    assert decision.status.state == State.COMPARED
    #assert len(decision.data[0].moves.base) + len(decision.data[0].moves.possible) == 4  # head + tail = SPRDIST
