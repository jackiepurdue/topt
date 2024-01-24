import subprocess
from typing import List

_file = "../lib/rspr"


def run_default(trees: List[str]):
    """
    TODO: Refactor, and find a way to get moves and MAF at the same time without running 2x
    """
    return subprocess.run(
        [_file, "-fpt"],
        stdout=subprocess.PIPE,
        input=(trees[0] + "\n" + trees[1]).encode('utf-8')
    ).stdout.decode('utf-8')


def run_with_show_moves(trees: List[str]):
    """
    TODO: Refactor, and find a way to get moves and MAF at the same time without running 2x
    """
    return subprocess.run(
        [_file, "-fpt", "-show_moves"],
        stdout=subprocess.PIPE,
        input=(trees[0] + "\n" + trees[1]).encode('utf-8')
    ).stdout.decode('utf-8')
