# from map import nodes
from random import choice


def random_xy(nodes: list) -> tuple:
    return choice(tuple(nodes))
