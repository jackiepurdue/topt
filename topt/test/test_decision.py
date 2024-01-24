import pytest

from topt.topt import Move, Record, MoveGroup, Status, State, Decision
import topt.topt as topt


@pytest.fixture
def sample_moves():
    move_0 = Move(source={"a", "b"}, target={"c", "d"})
    move_1 = Move(source={"e", "f"}, target={"g", "h"})
    move_2 = Move(source={"i", "j"}, target={"k", "l"})
    move_4 = Move(source={"a", "b"}, target={"c", "d"})
    return [move_0, move_1, move_2, move_4]


@pytest.fixture
def sample_trees():
    tree_0_newick = "(((a,b),(c,d)),(e,f));"
    tree_1_newick = "(((a,b),(c,d)),(e,f));"
    tree_0 = topt.generate_tree_node_from_newick(tree_0_newick)
    tree_1 = topt.generate_tree_node_from_newick(tree_1_newick)
    return [tree_0, tree_1]


@pytest.fixture
def sample_decision_records(sample_moves, sample_trees):
    record_0 = Record(
        node=sample_trees[0],
        moves=MoveGroup(
            applied=[sample_moves[0]],
            possible=[sample_moves[1], sample_moves[2]]
        ),
    )
    record_1 = Record(
        node=sample_trees[1],
        moves=MoveGroup(
            applied=[sample_moves[1]],
            possible=[sample_moves[0], sample_moves[2]])
    )
    record_2 = Record(
        node=sample_trees[1],
        moves=MoveGroup(
            applied=[sample_moves[1]],
            possible=[sample_moves[2], sample_moves[0]]
        )
    )
    return [record_0, record_1, record_2]


@pytest.fixture
def sample_decision_node(sample_decision_records):
    solution_state_0 = Status(100.0, State.START)

    decision_node_0 = Decision(
        data=[sample_decision_records[0]],
        status=solution_state_0,
        children=[]
    )

    solution_state_1 = Status(1.0, State.EXPANDING)

    decision_node_1 = Decision(
        data=[sample_decision_records[0], sample_decision_records[2]],
        status=solution_state_1,
        children=[]
    )

    solution_state_2 = Status(10.0, State.EXPANDING)

    decision_node_2 = Decision(
        data=[sample_decision_records[0],
              sample_decision_records[1],
              sample_decision_records[2]],
        status=solution_state_2,
        children=[decision_node_0, decision_node_1]
    )

    solution_state_3 = Status(0.0, State.REVERSING)

    decision_node_3 = Decision(
        data=[sample_decision_records[0]],
        status=solution_state_3,
        children=[]
    )

    solution_state_4 = Status(100.0, State.START)

    decision_node_4 = Decision(
        data=[sample_decision_records[0]],
        status=solution_state_4,
        children=[decision_node_3, decision_node_2]
    )

    return decision_node_4


def test_move(sample_moves):
    assert sample_moves[0].source == {"a", "b"}
    assert sample_moves[0].target == {"c", "d"}
    assert sample_moves[1] != sample_moves[0]
    assert sample_moves[0] == sample_moves[3]


def test_decision_record(sample_decision_records):
    record1 = sample_decision_records[0]
    assert record1.node is not None
    assert len(record1.moves.applied) == 1
    assert len(record1.moves.possible) == 2


def test_decision_node(sample_decision_node):
    node = sample_decision_node
    assert node.status.value == 100.0
    assert node.status.state == State.START
    assert len(node.children) == 2
    assert len(node.data) == 1
    assert isinstance(node.data[0], Record)


def test_initialize_comparison_decision(sample_trees):
    decision_node = topt.make_start_comparison_decision(sample_trees[0], sample_trees[1])

    assert isinstance(decision_node, Decision)
    assert len(decision_node.children) == 0
    assert decision_node.status.value == 0.0
    assert decision_node.status.state == State.START

    assert isinstance(decision_node.data[0], Record)
    assert decision_node.data[0].node == sample_trees[0]
    assert decision_node.data[0].moves.applied == []
    assert decision_node.data[0].moves.possible == []
    assert decision_node.data[0].moves.base == []

    assert isinstance(decision_node.data[1], Record)
    assert decision_node.data[1].node == sample_trees[0]
    assert decision_node.data[1].moves.applied == []
    assert decision_node.data[1].moves.possible == []
    assert decision_node.data[1].moves.base == []
