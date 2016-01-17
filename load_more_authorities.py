import py2neo

from app.db_comm import graph
from app.entity_iterators import get_authorities


def to_node(authority):
    return py2neo.Node(*authority.labels, **authority.properties)


for i in range(300):
    graph.create(
        *[to_node(authority) for authority in get_authorities(from_id=200000 + 100000 * i, to_id=210000 + 100000 * i)])
    print('yo')
