import py2neo
from app import primo_comm

py2neo.authenticate("localhost:7474", "neo4j", "123456")
graph = py2neo.Graph()
# graph.schema.create_uniqueness_constraint("Record", "recordid")
for result, _ in zip(primo_comm.Results("בן גוריון", 30), range(40)):
    properties = {'recordid': result['control']['recordid'], 'data': str(result)}
    graph.create(py2neo.Node("Record", **properties))
