from typing import List

import pytest

from topt.topt import Status, Record, Decision, State
import topt.topt as topt

@pytest.fixture
def matched_decision():
    t1 = topt.generate_tree_node_from_newick("(a,(b,c));")
    t2 = topt.generate_tree_node_from_newick("(c,(a,b));")
    return Decision(data=[Record(node=t1), Record(node=t2)], status=Status(state=State.MATCHED))


@pytest.fixture
def single_tree_decision():
    t1 = topt.generate_tree_node_from_newick("(a,(b,c));")
    return Decision(data=[Record(node=t1)], status=Status(state=State.START))


@pytest.fixture
def disjoint_decision():
    t1 = topt.generate_tree_node_from_newick("(a,(b,c));")
    t2 = topt.generate_tree_node_from_newick("(d,(e,f));")
    return Decision(data=[Record(node=t1), Record(node=t2)], status=Status(state=State.START))


@pytest.fixture
def all_intersecting_decision():
    t1 = topt.generate_tree_node_from_newick("(a,(b,c));")
    t2 = topt.generate_tree_node_from_newick("(b,(c,a));")
    return Decision(data=[Record(node=t1), Record(node=t2)], status=Status(state=State.START))


@pytest.fixture
def some_intersecting_decision():
    t1 =topt.generate_tree_node_from_newick("((a,(b,c)),d);")
    t2 =topt.generate_tree_node_from_newick("(b,(c,a));")
    return Decision(data=[Record(node=t1), Record(node=t2)], status=Status(state=State.START))


@pytest.fixture
def some_intersecting_reverse_decision():
    t1 =topt.generate_tree_node_from_newick("(b,(c,a));")
    t2 =topt.generate_tree_node_from_newick("((a,(b,c)),d);")
    return Decision(data=[Record(node=t1), Record(node=t2)], status=Status(state=State.START))
