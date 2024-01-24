from django.http import JsonResponse
import topt.topt as topt
from topt.topt import Record, Status, Decision, State
from topt.topt.ilp import Ilp


def api(request):
    with open('./test/files/tree_examples_2', 'r') as f:
        lines = f.readlines()

    comparisons = []
    for line in lines:
        tuple_strs = line.split(' ')
        l = tuple_strs[0].replace('\n', '')
        r = tuple_strs[1].replace('\n', '')
        comparisons.append((l, r))


    ilp_paths = []
    json_paths = {}
    index =0
    for comparison in comparisons:
        data_record = [
            Record(topt.generate_tree_node_from_newick((comparison[0]))),
            Record(topt.generate_tree_node_from_newick(comparison[1]))
        ]

        decision = topt.make_comparison_decision(
            data=data_record,
            make_decision_fns=[
                topt.make_match_comparison_decision,
                topt.make_compare_get_moves_decision,
                topt.make_multiple_move_expander_decision,
                topt.make_reverse_spd_moves_decision,
                topt.make_all_edge_decision,
                topt.make_complete_tree_decision
            ]
        )

        json_decisions = {}
        topt.traverse_decisions_get_all(decision, json_decisions)
        json_decision_tree = topt.build_decision_json(decision)
        path_json = {
            "data": json_decisions,
            "decision_nodes": json_decision_tree
        }

        json_paths[index] = path_json
        index = index + 1

        final_decisions = [d for d in topt.get_all_nodes(decision) if not d.children]
        ilp_paths.append(final_decisions)

    #ilp = Ilp(ilp_paths)
    #ilp.solve()

    return JsonResponse(json_paths)


