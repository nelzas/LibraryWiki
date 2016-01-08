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
        records_list = {'author_of' : {}, 'subject_of' : {}}
        print("%s records" % len(records))
        for record in records:
            record_data = eval(record.node['data'])
            record_control = record_data['control']
            record_display = record_data['display']
            record_type = record_display['type']
            record_fields = {
                'nnl' : record_control['sourcerecordid'],
                'nnl_prefix' : record_control['sourceid'],
                'title' : record.node['title'],
                'description' : record.node['title'], # TODO: same as title?
                'date' : record_display.get('creationdate', 'לא ידוע'),
                'notes' : record_display.get('lds05',[""]),
            }
            rel_type = record.rel_type # either author_of or subject_of
            # create_page_from_dictionary(record_dict)
            if record_type not in records_list[rel_type]:
                records_list[rel_type][record_type] = []
            records_list[rel_type][record_type].append(record_fields)
        try:
            create_page_from_node(person_node, records_list)
        except Exception as e:
            print(e)
