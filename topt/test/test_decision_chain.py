from topt.topt import Record, Status, State
import topt.topt as topt


# TODO: There are some assertions that need to be revised (commented out) due to a labeling change


def test_make_unit_decision_basic_functionality():
    data_record = [Record(topt.create_leaf_tree_node("a")), Record(topt.create_leaf_tree_node("b"))]
    decision = topt.make_unit_decision(data=data_record, make_decision_fns=[])
    assert decision.data == data_record
    assert decision.status == Status()
    assert decision.children == []


def test_make_unit_decision_with_children():
    data_record = [Record(topt.create_leaf_tree_node("b"))]
    # child_decision = topt.make_single_decision_old([Record(topt.create_leaf_tree_node("b"))])
    decision = topt.make_unit_decision(
        data_record,
        Status(),
        [
            topt.make_unit_decision,
            topt.make_unit_decision,
            topt.make_unit_decision,
            topt.make_unit_decision
        ]
    )
    assert decision.data == data_record
    assert decision.status == Status()
    assert len(decision.children) == 1
    assert len(decision.children[0].children) == 1
    assert len(decision.children[0].children[0].children) == 1
    assert len(decision.children[0].children[0].children[0].children) == 1
    assert decision.children[0].data == [Record(topt.create_leaf_tree_node("b"))]
    assert decision.children[0].children[0].data == [Record(topt.create_leaf_tree_node("b"))]
    assert decision.children[0].children[0].children[0].data == [Record(topt.create_leaf_tree_node("b"))]
    assert decision.children[0].children[0].children[0].children[0].data == [Record(topt.create_leaf_tree_node("b"))]


def test_make_start_comparison_decision_basic_functionality():
    data_record = [Record(topt.create_leaf_tree_node("a")), Record(topt.create_leaf_tree_node("b"))]
    decision = topt.make_comparison_decision(data=data_record, make_decision_fns=[])
    assert decision.data == data_record
    assert decision.status == Status(state=State.START)
    assert decision.children == []


def test_make_start_comparison_decision_with_children():
    data_record = [Record(topt.create_leaf_tree_node("a")), Record(topt.create_leaf_tree_node("b"))]
    # child_decision = topt.make_single_decision_old([Record(topt.create_leaf_tree_node("b"))])
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_comparison_decision,
            topt.make_comparison_decision
        ]
    )
    assert decision.data == data_record
    assert decision.status == Status(state=State.START)
    assert len(decision.children) == 1
    assert len(decision.children[0].children) == 1
    assert decision.children[0].children[0].status == Status(state=State.START)
    assert decision.children[0].data == [Record(topt.create_leaf_tree_node("a")),
                                         Record(topt.create_leaf_tree_node("b"))]
    assert decision.children[0].children[0].data == [Record(topt.create_leaf_tree_node("a")),
                                                     Record(topt.create_leaf_tree_node("b"))]


def test_make_match_comparison_decision_basic_functionality():
    data_record = [Record(topt.create_leaf_tree_node("a")), Record(topt.create_leaf_tree_node("a"))]
    decision = topt.make_match_comparison_decision(data=data_record, make_decision_fns=[])
    #######################################################################################3assert decision.data == data_record
    assert decision.status == Status(state=State.MATCHED)
    assert decision.children == []


def test_make_match_comparison_decision_with_children():
    data_record = [Record(topt.create_leaf_tree_node("a")), Record(topt.create_leaf_tree_node("a"))]
    # child_decision = topt.make_single_decision_old([Record(topt.create_leaf_tree_node("b"))])
    decision = topt.make_match_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_match_comparison_decision
        ]
    )
    ##############################################################################################    assert decision.data == data_record
    assert decision.status == Status(state=State.MATCHED)
    assert len(decision.children) == 1
    # this should be invalid it needs a start state
    assert decision.children[0].status.state == State.INVALID


def test_make_match_comparison_decision_invalid_disjoint():
    data_record = [Record(topt.create_leaf_tree_node("a")), Record(topt.create_leaf_tree_node("b"))]
    decision = topt.make_match_comparison_decision(data=data_record, make_decision_fns=[])
    assert decision.status == Status(state=State.INVALID)


def test_make_match_comparison_decision_invalid_one_record():
    data_record = [Record(topt.create_leaf_tree_node("a"))]
    decision = topt.make_match_comparison_decision(data=data_record, make_decision_fns=[])
    assert decision.status == Status(state=State.INVALID)


def test_make_start_then_match_comparison_decision():
    data_record = [
        Record(topt.generate_tree_node_from_newick(("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision
        ]
    )
    print(topt.generate_newick(decision.children[0].data[0].node))
    print(topt.generate_newick(decision.children[0].data[1].node))
    l1 = topt.get_leaf_nodes(decision.children[0].data[0].node)
    l2 = topt.get_leaf_nodes(decision.children[0].data[1].node)

    assert {n.data.label for n in l1} == {n.data.label for n in l2}


def test_make_start_then_match_then_rspr_comparison_decision():
    data_record = [
        Record(topt.generate_tree_node_from_newick(("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_compare_get_moves_decision
        ]

    )

    matched_leaves = topt.get_leaf_nodes(decision.children[0].data[0].node)
    matched_leaves_2 = topt.get_leaf_nodes(decision.children[0].data[1].node)
    assert {n.data.label for n in matched_leaves} == {n.data.label for n in matched_leaves_2}
    print()

    rspr_tree_node = decision.children[0].children[0].data[0].node
    matched_original = decision.children[0].data[0].node
    ########################################################################3assert topt.generate_newick(rspr_tree_node) == topt.generate_newick(topt.label_tree(matched_original, 0)) #labeled


def test_make_start_then_match_then_rspr_then_do_recursion_comparison_decision_singular():
    data_record = [
        Record(topt.generate_tree_node_from_newick(("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_compare_get_moves_decision,
            topt.make_single_move_expander_decision
        ]
    )

    matched_leaves = topt.get_leaf_nodes(decision.children[0].data[0].node)
    matched_leaves_2 = topt.get_leaf_nodes(decision.children[0].data[1].node)
    assert {n.data.label for n in matched_leaves} == {n.data.label for n in matched_leaves_2}

    rspr_tree_node = decision.children[0].children[0].data[0].node
    matched_original = decision.children[0].data[0].node
    ##############################################################assert topt.generate_newick(rspr_tree_node) == topt.generate_newick(topt.label_tree(matched_original, 0)) #labeled
    intitial_moves = decision.children[0].children[0].data[0].moves
    final_moves = decision.children[0].children[0].children[0].children[0].children[0].children[0].data[0].moves
    #assert intitial_moves.possible + intitial_moves.base == final_moves.applied


def test_make_start_then_match_then_rspr_then_do_recursion_comparison_decision_multiple():
    """    Record(topt.generate_tree_node_from_newick(("((a,b),((c,(d,e)),(f,g)));"))),
        Record(topt.generate_tree_node_from_newick("(a,(b,((((c,d),e),f),g)));"))]
        data_record = [
        Record(topt.generate_tree_node_from_newick(("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));"))),
    Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    '((((a,b),(c,d)),(e,f)),(g,(h,i)));'), ('(a,((b,c),(((d,e),f),((g,h),i))));'"""
    data_record = [
        Record(topt.generate_tree_node_from_newick("((((a,b),(c,d)),(e,f)),(g,(h,i)));")),
        Record(topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));"))]
    decision = topt.make_comparison_decision(
        data_record,
        Status(),
        [
            topt.make_match_comparison_decision,
            topt.make_compare_get_moves_decision,
            topt.make_multiple_move_expander_decision
        ]
    )

    matched_leaves = topt.get_leaf_nodes(decision.children[0].data[0].node)
    matched_leaves_2 = topt.get_leaf_nodes(decision.children[0].data[1].node)
    assert {n.data.label for n in matched_leaves} == {n.data.label for n in matched_leaves_2}

    rspr_tree_node = decision.children[0].children[0].data[0].node
    matched_original = decision.children[0].data[0].node
    ##############################################################assert topt.generate_newick(rspr_tree_node) == topt.generate_newick(topt.label_tree(matched_original, 0)) #labeled
    intitial_moves = decision.children[0].children[0].data[0].moves
    final_moves = decision.children[0].children[0].children[0].children[0].children[0].children[0].data[0].moves
  #  assert intitial_moves.possible + intitial_moves.base == final_moves.applied



def test_make_start_then_match_then_rspr_then_do_recursion_comparison_decision_multiple_then_do_reverse():
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
            topt.make_reverse_spd_moves_decision
        ]
    )

    matched_leaves = topt.get_leaf_nodes(decision.children[0].data[0].node)
    matched_leaves_2 = topt.get_leaf_nodes(decision.children[0].data[1].node)
    assert {n.data.label for n in matched_leaves} == {n.data.label for n in matched_leaves_2}

    rspr_tree_node = decision.children[0].children[0].data[0].node
    matched_original = decision.children[0].data[0].node
    ##############################################################assert topt.generate_newick(rspr_tree_node) == topt.generate_newick(topt.label_tree(matched_original, 0)) #labeled
    intitial_moves = decision.children[0].children[0].data[0].moves
    final_moves = decision.children[0].children[0].children[0].children[0].children[0].children[0].data[0].moves
  #  assert intitial_moves.possible + intitial_moves.base == final_moves.applied
