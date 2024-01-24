from topt.topt.data import Move


def _strip(s: str):
    """
    TODO: Refactor
    """
    return s.strip()


def parse_ancestor_moves(rspr_output: str):
    """
    TODO: Refactor
    """
    list_output = rspr_output.split('\n')
    list_output = list(filter(lambda line: line, list_output[3:]))

    source_to_destination_tuples = []
    i = 0
    while i < len(list_output) - 1:
        if i % 2 == 1:
            source_to_destination_tuples.append(
                (set(map(_strip, list_output[i].split(':')[0].split(','))),
                 set(map(_strip, list_output[i].split(':')[1].split(',')))
                 )
            )
        i = i + 1

    return [Move(stm[0], stm[1]) for stm in source_to_destination_tuples]


def parse_forest(rspr_output: str):
    """
    TODO: Refactor
    """
    newick_forest = rspr_output.split('\n')
    newick_forest = newick_forest[-3]
    newick_forest = newick_forest.split(':')[1].split(" ")
    newick_forest = [nwk+";" for nwk in newick_forest if nwk != ""]


    return newick_forest
