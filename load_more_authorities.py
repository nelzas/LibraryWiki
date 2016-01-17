import py2neo

from app.db_comm import graph
from app.entity_iterators import get_authorities


def to_node(authority):
    return py2neo.Node(*authority.labels, **authority.properties)


for i in range(3000):
    graph.create(
        *[to_node(authority) for authority in get_authorities(from_id=200000 + 1000 * i, to_id=201000 + 1000 * i)])
    print('yo')
