import py2neo
import re
from app import primo_comm
from app.authorities import db_auth
from app.settings import *
from py2neo.packages.httpstream import http

http.socket_timeout = 9999

py2neo.authenticate(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
graph = py2neo.Graph('http://' + NEO4J_URL + NEO4J_GRAPH)


def set_records():
    # graph.schema.create_uniqueness_constraint("Record", "recordid")
    for result, _ in zip(primo_comm.Results("בן גוריון", 200), range(100)):
        properties = {'recordid': result['control']['recordid'], 'data': str(result),
                      'title': result['display']['title']}
        m = graph.merge_one("Record", "recordid", properties['recordid'])
        m.properties.update(**properties)
        m.labels.add(result['display']['type'])
        m.push()


def set_authorities():
    # graph.schema.create_uniqueness_constraint("Authority", "id")
    for authority, _ in zip(db_auth(), range(200)):
        m = graph.merge_one("Authority", "id", authority["id"])
        m.properties.update(**authority)
        type_of_record = authority.get('type')
        if type_of_record:
            m.labels.add(type_of_record.title())
        m.push()


def create_relationship(authorities, record, relation):
    if not authorities:
        return
    for authority in authorities:
        node = graph.merge_one("Authority", "id", authority)
        graph.create_unique(py2neo.Relationship(node, relation, record))


def create_records_authorities_relationships():
    records = graph.cypher.execute("match (n:Record) return n as node, n.data as data")
    for record in records:
        if not record.data:
            continue
        authors, subjects = authorities_of_record(eval(record.data)['browse'])
        create_relationship(authors, record.node, 'author_of')
        create_relationship(subjects, record.node, 'subject_of')
    graph.push()


def authorities_of_record(authorities):
    find_id = re.compile(r'INNL\d{11}\$\$').search

    def extract_authority(relationship):
        return authorities.get(relationship) and {find_id(authority).group()[6:-2] for authority in
                                                  authorities[relationship] if find_id(authority)}

    authors_set = extract_authority('author')
    subjects_set = extract_authority('subject')
    return authors_set, subjects_set


print("setting records...")
set_records()
print("setting authorities...")
set_authorities()
print("creating relationships...")
create_records_authorities_relationships()
print("done!")
