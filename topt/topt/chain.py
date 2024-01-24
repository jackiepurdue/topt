from typing import List, Callable

from topt.topt import Record, Status, Decision, State, MoveGroup, Move
import topt.topt as topt
import topt.topt.private.ext as _p


def make_unit_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    # do stuff
    if make_decision_fns:
        create_child = make_decision_fns[0]
        return Decision(data=data, status=status, children=[
            create_child(data, status, make_decision_fns[1:])  # normally new values
        ])
    else:
        return Decision(data, status, [])


def make_invalid_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    new_status = Status(state=State.INVALID)
    if make_decision_fns:
        create_child = make_decision_fns[0]
        return Decision(data=data, status=new_status, children=[
            create_child(data, new_status, make_decision_fns[1:])  # normally new values
        ])
    else:
        return Decision(data, new_status, [])


def make_comparison_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    new_status = Status(state=State.START)
    if make_decision_fns:
        create_child = make_decision_fns[0]
        return Decision(data=data, status=new_status, children=[
            create_child(data, new_status, make_decision_fns[1:])  # normally new values
        ])
    else:
        return Decision(data, new_status, [])


def make_match_comparison_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    if status.state == State.START and len(data) == 2:
        variant_tree = data[0]
        base_tree = data[1]

        matched_status = Status(state=State.MATCHED)
        matched_tree = topt.match_tree_labels(variant_tree.node, base_tree.node)
        if not matched_tree:
            return make_invalid_decision(data=data, status=status,
                                         make_decision_fns=make_decision_fns[1:])
        new_records = [
            Record(node=matched_tree[0]),
            Record(node=matched_tree[1]),
            Record(node=variant_tree.node),  # pass along the original reference tree
        ]

        if make_decision_fns:
            create_child = make_decision_fns[0]
            return Decision(data=new_records, status=matched_status, children=[
                create_child(new_records, matched_status, make_decision_fns[1:])  # normally new values
            ])
        else:
            return Decision(new_records, matched_status, [])
    else:
        return make_invalid_decision(data=data, status=status, make_decision_fns=make_decision_fns[1:])


def make_compare_get_moves_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    if len(data) == 3 and status.state == State.MATCHED:
        print(f"retrieving moves from rSPR")
        tree1 = data[0].node
        tree2 = data[1].node
        original_variant_tree = data[2].node
        result_str = topt.run_with_show_moves([topt.generate_newick(tree1), topt.generate_newick(tree2)])
        all_moves = _p.parse_ancestor_moves(result_str)
        result_str_default = topt.run_default([topt.generate_newick(tree1), topt.generate_newick(tree2)])
        forest = _p.parse_forest(result_str_default)

        forest_tree_nodes = [topt.label_tree(topt.generate_tree_node_from_newick(nwk), 0) for nwk in forest]


        print()
        # get a deleted version of the ref tree (variant) label the tree before starting
        prepared_start_tree = topt.add_outgroup(topt.label_tree(topt.match_tree_labels_with_delete(original_variant_tree, tree1)[0], 0), topt.create_leaf_tree_node("X"))
        new_records = [Record(
            node=prepared_start_tree,
            moves=MoveGroup(
                base=all_moves[1:],
                possible=[all_moves[0]]
            )
        )]

        cur_records = [Record(
            node=topt.label_tree(tree1, 0),
        ),Record(
            node=topt.label_tree(tree2, 0)
        )]

        for member in forest_tree_nodes:
            cur_records.append(
                Record(
                    node=member
                )
            )

        new_status = Status(
            state=State.COMPARED
        )

        if make_decision_fns:
            create_child = make_decision_fns[0]

            return Decision(
                data=cur_records,
                status=new_status,
                children=[create_child(new_records, new_status, make_decision_fns[1:])]
            )
        else:
            return Decision(cur_records, new_status, [])
    else:
        return make_invalid_decision(data=data, status=status,
                                     make_decision_fns=make_decision_fns[1:])


def make_single_move_expander_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    tree = data[0].node
    if status.state == State.COMPARED or status.state == State.EXPANDING:
        # do stuff with move to transform tree and branch on possbiites

        tree = data[0].node  # to be transformed
        move = data[0].moves.possible[0]  # single move

        actual_move = topt.get_node_label_move(tree, move)

        new_node, parent_of_new_node = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree, actual_move)
        new_applied = data[0].moves.applied + data[0].moves.possible
        new_base = data[0].moves.base[1:]
        new_possible = [data[0].moves.base[0]] if len(data[0].moves.base) > 0 else []
        # remaining_moves = moves[1:]

        # result_str = run([util.generate_newick(tree1), util.generate_newick(tree2)])
        # all_moves = _p.parse_ancestor_moves(result_str)

        new_records = [Record(
            node=new_node,
            moves=MoveGroup(
                applied=new_applied,
                possible=new_possible,
                base=new_base
            )
        )]

        new_status = Status(
            state=State.EXPANDING
        )

        if make_decision_fns and len(new_possible) == 0:  # condition for stop
            create_child = make_decision_fns[0]

            return Decision(
                data=new_records,
                status=new_status,
                children=[create_child(new_records, new_status, make_decision_fns[1:])]
            )
        elif not make_decision_fns and len(new_possible) == 0:  # condition for stop
            #     create_child = make_decision_fns[0]

            return Decision(
                data=new_records,
                status=new_status,
                children=[]
            )
        elif len(new_possible) > 0:
            return Decision(
                data=new_records,
                status=new_status,
                children=[make_single_move_expander_decision(
                    data=new_records,
                    status=new_status,
                    make_decision_fns=make_decision_fns  # keep them as they are for entirety of recursion
                )]
            )
        else:
            return make_invalid_decision(data=data, status=status,
                                         make_decision_fns=make_decision_fns[1:])
    else:
        return make_invalid_decision(data=data, status=status,
                                     make_decision_fns=make_decision_fns[1:])


def make_multiple_move_expander_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    tree = data[0].node
    if status.state == State.COMPARED or status.state == State.EXPANDING:
        print(f"Applying SPD move for decision {data[0].moves.possible}")
        # do stuff with move to transform tree and branch on possbiites

        tree = data[0].node  # to be transformed
        move = data[0].moves.possible[0]  # single move

        # actual_move = topt.get_node_label_move(tree, move)
        all_moves = topt.get_possible_moves_from_move(tree, move)

        cur_records = [Record(
            node=tree,
            moves=MoveGroup(
                applied=data[0].moves.applied,
                possible=all_moves,
                base=data[0].moves.base
            )
        )]
        # new_node, parent_of_new_node = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree, actual_move)

        new_possible = [data[0].moves.base[0]] if len(data[0].moves.base) > 0 else []

        # all_moves = topt.get_possible_moves_from_move(tree, move)
        all_new_records = []

        for move in all_moves:
            new_node, last_source_parent = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree, move)
            # applied in this case will store the reversing moves

            actual_applied = Move(
                {topt.find_common_ancestor(tree, move.source).data.label},
                {topt.find_common_ancestor(tree, move.target).data.label}
            )  # nothing to be done with it

            reverse_move = Move(actual_applied.source, {last_source_parent.data.label})

            new_reverse = [reverse_move] + data[0].moves.reverse

            #TODO: Important for getting the applied move for a target... it goes above the newly created node, and we make it here
            #actually the bug still exists here. theres somethign else going on
            # prety sure its just that the rendering needs to send the target arrow to the node and the pink nodes do not get x32424 children added.
            target_of_last_applied = None
            #if data[0].moves.applied:
            #target_of_last_applied = topt.find_common_ancestor(tree, move.target)
            #source_set_of_last_applied = data[0].moves.applied[len(data[0].moves.applied) - 1].source
            #adjusted_applied_target = topt.get_parent(new_node, target_of_last_applied).data.label
            #actual_applied = Move(
            #    {topt.find_common_ancestor(tree, move.source).data.label},
            #    {adjusted_applied_target}
            #)

            new_applied = [actual_applied] + data[0].moves.applied
            new_base = data[0].moves.base[1:]

            all_new_records.append([Record(
                node=new_node,
                moves=MoveGroup(
                    applied=new_applied,
                    possible=new_possible,
                    base=new_base,
                    reverse=new_reverse
                )
            )])

            new_status = Status(
                state=State.EXPANDING
            )

        if make_decision_fns and len(new_possible) == 0:  # condition for stop
            create_child = make_decision_fns[0]
            child_decisions = []
            for records in all_new_records:
                adjusted_records = [
                    Record(
                        node=records[0].node,
                        moves=MoveGroup(
                            applied=records[0].moves.applied,
                            possible=[records[0].moves.reverse[0]],
                            base=records[0].moves.base,
                            reverse=records[0].moves.reverse[1:]
                        )
                    )
                ]

                child_decisions.append(Decision(
                    data=adjusted_records,
                    status=Status(state=State.EXPANDED),
                    children=[create_child(adjusted_records, Status(state=State.EXPANDED), make_decision_fns[1:])]
                    # keep them as they are for entirety of recursion
                ))
            return Decision(
                data=cur_records,
                status=Status(state=State.EXPANDING),
                children=child_decisions
            )
        elif not make_decision_fns and len(new_possible) == 0:  # condition for stop
            #     create_child = make_decision_fns[0]

            return Decision(
                data=cur_records,
                status=Status(state=State.EXPANDED),
                children=[]
            )
        elif len(new_possible) > 0:
            child_decisions = []
            for records in all_new_records:
                child_decisions.append(make_multiple_move_expander_decision(
                    data=records,
                    status=Status(state=State.EXPANDING),
                    make_decision_fns=make_decision_fns  # keep them as they are for entirety of recursion
                ))
            return Decision(
                data=cur_records,
                status=Status(state=State.EXPANDING),
                children=child_decisions
            )
        else:
            return make_invalid_decision(data=data, status=status,
                                         make_decision_fns=make_decision_fns[1:])
    else:
        return make_invalid_decision(data=data, status=status,
                                     make_decision_fns=make_decision_fns[1:])


def make_reverse_spd_moves_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    tree = data[0].node
    if status.state == State.REVERSING or status.state == State.EXPANDED:
        # do stuff with move to transform tree and branch on possbiites

        tree = data[0].node  # to be transformed

        tree = tree
        reverse_move = data[0].moves.possible[0] if len(data[0].moves.possible) > 0 else Move({}, {})
        new_tree = topt.reverse_subtree_ungraft_and_regraft_single_labeled_move(tree, reverse_move)
        new_records = [Record(
            node=new_tree,
            moves=MoveGroup(
                applied=data[0].moves.applied,  # for now just same
                possible=[data[0].moves.reverse[0]] if len(data[0].moves.reverse) > 0 else [],
                base=[],
                reverse=data[0].moves.reverse[1:]
            )
        )]

        new_status = Status(
            state=State.REVERSING
        )

        if make_decision_fns and len(data[0].moves.reverse) == 0:  # condition for stop
            create_child = make_decision_fns[0]

            return Decision(
                data=new_records,
                status=new_status,
                children=[create_child(new_records, new_status, make_decision_fns[1:])]
            )
        elif not make_decision_fns and len(data[0].moves.reverse) == 0:  # condition for stop
            #     create_child = make_decision_fns[0]

            return Decision(
                data=new_records,
                status=new_status,
                children=[]
            )
        elif len(data[0].moves.reverse) > 0:
            return Decision(
                data=new_records,
                status=new_status,
                children=[make_reverse_spd_moves_decision(
                    data=new_records,
                    status=new_status,
                    make_decision_fns=make_decision_fns  # keep them as they are for entirety of recursion
                )]
            )
        else:
            return make_invalid_decision(data=data, status=status,
                                         make_decision_fns=make_decision_fns[1:])
    else:
        return make_invalid_decision(data=data, status=status,
                                     make_decision_fns=make_decision_fns[1:])


def make_all_edge_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    # do stuff

    new_status = Status(
        state=State.REVERSED,
    )

    if make_decision_fns:
        create_child = make_decision_fns[0]
        return Decision(data=data, status=new_status, children=[
            create_child(data, new_status, make_decision_fns[1:])  # normally new values
        ])
    else:
        return Decision(data, new_status, [])


# temporarily using complete_tree
def make_complete_tree_decision(
        data: List[Record],
        status: Status = Status(),
        make_decision_fns: List[Callable[[List[Record], Status], Decision]] = []
) -> Decision:
    # do stuff
    new_records = [Record(
        node=topt.complete_tree(data[0].node, 0)[0],
        moves=MoveGroup(
            applied=data[0].moves.applied,  # for now just same
            possible=data[0].moves.possible,
            base=data[0].moves.base,
            reverse=data[0].moves.reverse
        )
    )]
    new_status = Status(
        state=State.FINISH,
    )

    if make_decision_fns:
        create_child = make_decision_fns[0]
        return Decision(data=new_records, status=new_status, children=[
            create_child(new_records, new_status, make_decision_fns[1:])  # normally new values
        ])
    else:
        return Decision(new_records, new_status, [])
