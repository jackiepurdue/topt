from typing import List, Dict

from pulp import LpVariable, LpProblem, GLPK, LpStatus, LpMaximize


class Ilp:

    def __init__(self, data: List[Dict]):
        self.data = data

    def solve(self):

        data =self.data

        edge_table = {}
        lp_all = []
        tree_index = 0
        for tree_move_data in data:
            lp_move_sequence_decisions_for_tree = []
            move_sequence_index = 0
            for move_sequence in tree_move_data:
                moves = move_sequence.data[0].moves.applied
                lp_move_sequence = []

                for move in moves:
                    source = move.source.copy().pop() #TODO: fix this really bad idea (all related to the labeling problems)
                    if len(source) > 5:
                        source = source[:5]
                    target = move.target.copy().pop() #TODO: fix this really bad idea
                    if len(target) > 5:
                        target = target[:5]
                    lp_variable = LpVariable("source."+source+"_target."+target+"_move."+str(move_sequence_index)+"_tree." + str(tree_index), 0, 1, cat="Binary")
                    lp_move_sequence.append(lp_variable)

                    tedge = source+"_"+target
                    if tedge not in edge_table:
                        edge_table[tedge] = []
                        edge_table[tedge].append(lp_variable)
                    else:
                        edge_table[tedge].append(lp_variable)
                lp_move_sequence.append(LpVariable("z_p" + str(move_sequence_index) + "_tree." + str(tree_index), 0, len(lp_move_sequence), cat="Integer"))
                lp_move_sequence.append(LpVariable("b_p" + str(move_sequence_index) + "_tree." + str(tree_index) + ".1", 0, 1, cat="Binary"))
                lp_move_sequence.append(LpVariable("b_p" + str(move_sequence_index) + "_tree." + str(tree_index) + ".2", 0, 1, cat="Binary"))

                lp_move_sequence_decisions_for_tree.append(lp_move_sequence)
                move_sequence_index = move_sequence_index + 1
            lp_all.append(lp_move_sequence_decisions_for_tree)
            tree_index = tree_index + 1

        lp_problem = LpProblem("tree_decisions", LpMaximize)

        for lp_move_sequence_decisions in lp_all:
            zs = None
            num_moves = None
            for lp_move_sequence in lp_move_sequence_decisions:
                z = lp_move_sequence[len(lp_move_sequence) - 3]
                b1 = lp_move_sequence[len(lp_move_sequence) - 2]
                b2 = lp_move_sequence[len(lp_move_sequence) - 1]
                num_moves = len(lp_move_sequence) - 3
                lp_problem += b1 + b2 == 1
                lp_problem += z <= 99999 * (1 - b1)
                lp_problem += z >= num_moves - 99999 * (1 - b2)
                lp_problem += z <= num_moves + 99999 * (1 - b2)
                zs += z

                moves = None
                moves_in_path_instance = lp_move_sequence[:len(lp_move_sequence)-3]
                for move in moves_in_path_instance:
                    moves += move

                lp_problem += moves == z
            lp_problem += zs == num_moves

        us = None
        for key in edge_table:
            # TODO: this number may be problematic later depending on data
            es = LpVariable("pesum_" + str(key), 0, 9999, cat="Integer")
            bin_bound = LpVariable("u_" + str(key), 0, 1, cat="Binary")

            us+= bin_bound #for optimization

            lp_problem += es <= 99999*(1-bin_bound)

            column = edge_table[key]
            edges_sum = None
            for edge in column:
                edges_sum += edge

            lp_problem += edges_sum == es

        lp_problem += us #objective

        print("Solving ILP:")
        print(lp_problem)
        status = lp_problem.solve(GLPK(msg=0))
        r = LpStatus[status]

        print(r)
        for var in lp_problem.variables():
            print(var.getName() + " = " + str(var.value()))
