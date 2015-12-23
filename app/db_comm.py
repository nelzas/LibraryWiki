import py2neo
from app import primo_comm
from app import authorities

py2neo.authenticate("104.155.27.166:7474", "neo4j", "R99R")
graph = py2neo.Graph("http://104.155.27.166:7474/db/data/")


def set_records():
    # graph.schema.create_uniqueness_constraint("Record", "recordid")
    for result, _ in zip(primo_comm.Results("בן גוריון", 30), range(40)):
        properties = {'recordid': result['control']['recordid'], 'data': str(result)}
        m = graph.merge_one("Record", "recordid", properties['recordid'])
        m.properties.update(**properties)
        m.push()


def set_authorities():
    # graph.schema.create_uniqueness_constraint("Authority", "id")
    for authority, _ in zip(authorities.db_auth(), range(100)):
        m = graph.merge_one("Authority", "id", authority["id"])
        m.properties.update(**authority)
        m.push()

set_authorities()
