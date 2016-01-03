import py2neo
from app import primo_comm
from app import authorities
from app.settings import *

py2neo.authenticate(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
graph = py2neo.Graph('http://' + NEO4J_URL + NEO4J_GRAPH)


def set_records():
    # graph.schema.create_uniqueness_constraint("Record", "recordid")
    for result, _ in zip(primo_comm.Results("בן גוריון", 200), range(1000)):
        properties = {'recordid': result['control']['recordid'], 'data': str(result),
                      'title': result['display']['title']}
        m = graph.merge_one("Record", "recordid", properties['recordid'])
        m.properties.update(**properties)
        m.labels.add(result['display']['type'])
        m.push()


def set_authorities():
    # graph.schema.create_uniqueness_constraint("Authority", "id")
    for authority, _ in zip(authorities.db_auth(), range(15000)):
        m = graph.merge_one("Authority", "id", authority["id"])
        m.properties.update(**authority)
        type = authority.get('type')
        if type:
            m.labels.add(type.title())
        m.push()


def create_relationship(authorities, record, relation):
    if not authorities:
        return
    for authority in authorities:
        node = graph.merge_one("Authority", "id", authority)
        graph.create(py2neo.Relationship(node, relation, record))


def create_records_authorities_relationships():
    records = graph.cypher.execute("match (n:Record) return n as node, n.data as data")
    for record in records:
        authors, subjects = authorities_of_record(eval(record.data)['browse'])
        create_relationship(authors, record.node, 'author_of')
        create_relationship(subjects, record.node, 'subject_of')
    graph.push()


def authorities_of_record(data):
    def extract_authority(key):
        if data.get(key):
            authorities_set = {authority.split('$$')[-2][5:] for authority in data[key] if
                               len(authority.split('$$')) > 1 and
                               len(authority.split('$$')[-2]) > 5 and authority.split('$$')[-2][5:].isdigit()} or None
        else:
            authorities_set = None
        return authorities_set

    authors_set = extract_authority('author')
    subjects_set = extract_authority('subject')
    return authors_set, subjects_set
