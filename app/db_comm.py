import py2neo
import re
from app.entity_iterators import Portraits, Photos, get_authorities, Results
from app.settings import *
from py2neo.packages.httpstream import http

http.socket_timeout = 9999

py2neo.authenticate(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
graph = py2neo.Graph('http://' + NEO4J_URL + NEO4J_GRAPH)


def get_entity_node(entity):
    return graph.merge_one(entity.labels[0], "id", entity.properties["id"])


def create_entity(entity):
    entity_node = get_entity_node(entity)
    entity_node.properties.update(**entity.properties)
    for label in entity.labels:
        entity_node.labels.add(label)
    entity_node.push()
    return entity_node


def set_entities(entities):
    for entity in entities:
        create_entity(entity)


def set_portraits():
    # people = graph.cypher.execute(
    #     "match (n:Person) where exists(n.person_name_absolute) return n.person_name_absolute as name, n as node")
    people = graph.cypher.execute(
        "match (n:Person) where n.id = '000091550' return n.person_name_absolute as name, n as node")
    for person in people:
        authority_portrait(person)


def authority_portrait(authority):
    query = authority.name
    portraits = Portraits(query)
    for portrait in portraits:
        portrait_node = create_entity(portrait)
        graph.create_unique(py2neo.Relationship(authority.node, "subject_of", portrait_node))
        graph.create_unique(py2neo.Relationship(authority.node, "portrait_of", portrait_node))


def set_photos():
    # people = graph.cypher.execute(
    #     "match (n:Person) where exists(n.person_name_heb) return n.person_name_heb as name, n as node")
    people = graph.cypher.execute(
        "match (n:Person) where n.id = '000091550' return n.person_name_heb as name, n as node")
    for person in people:
        authority_photos(person)


def authority_photos(authority):
    query = authority.name
    photos = Photos("מאיר, גולדה, 1898-1978")
    for photo in photos:
        portrait_node = create_entity(photo)
        graph.create_unique(py2neo.Relationship(authority.node, "subject_of", portrait_node))


def create_records_authorities_relationships():
    records = graph.cypher.execute("match (n:Record) return n as node, n.data as data")
    for record in records:
        if not record.data:
            continue
        authors, subjects = authorities_of_record(eval(record.data).get('browse'))
        create_relationship(authors, record.node, 'author_of')
        create_relationship(subjects, record.node, 'subject_of')
    graph.push()


def authorities_of_record(authorities):
    if not authorities:
        return
    authors_set = extract_authority('author', authorities)
    subjects_set = extract_authority('subject', authorities)
    return authors_set, subjects_set


def create_relationship(authorities, record, relation):
    if not authorities:
        return
    for authority in authorities:
        node = graph.merge_one("Authority", "id", authority)
        graph.create_unique(py2neo.Relationship(node, relation, record))


def extract_authority(relationship, authorities):
    find_id = re.compile(r"INNL\d{11}\$\$").search
    return authorities.get(relationship) and {find_id(authority).group()[6:-2] for authority in
                                              authorities[relationship] if find_id(authority)}

# set_entities(get_authorities())
# set_entities(Results('NNL_ALEPH'))
# create_records_authorities_relationships()
set_portraits()
set_photos()
