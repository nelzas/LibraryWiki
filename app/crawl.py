from app.settings import *
from app.pages import create_page_from_dictionary
from app.personality import create_page_from_node
import py2neo
import json


py2neo.authenticate(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
graph = py2neo.Graph('http://' + NEO4J_URL + NEO4J_GRAPH)
authorities = graph.cypher.execute('match (n:Person) where exists(n.person_name_heb) return n')
for person_nodes in authorities:
    for person_node in person_nodes:
        person_id = person_node['id']
        print("=============== " + person_id + " ================")
        print(person_node['person_name_heb'])
        person_json = json.loads(person_node['data'])
        print(person_json)
        records = graph.cypher.execute('match (p:Person {id:"' + person_id + '"})-[r]-(node) return type(r) as rel_type, node')
        record_ids = []
        for record in records:
            recordid = record.node['recordid']
            rel_type = record.rel_type
            print(rel_type + " : " + recordid)
            record_data = record.node['data']
            record_dict = eval(record_data)
            print(record_dict)
            # create_page_from_dictionary(record_dict)
            record_ids.append(recordid)
        print(record_ids)
        try:
            create_page_from_node(person_node)
        except Exception as e:
            print(e)
