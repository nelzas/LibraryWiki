from app.settings import *
from app.pages import create_page_from_dictionary
from app.personality import create_page_from_node
import py2neo
import json

py2neo.authenticate(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
graph = py2neo.Graph('http://' + NEO4J_URL + NEO4J_GRAPH)

PAGE_SIZE = 200
page_number = 0
record_count = 0
while True:
    skip = PAGE_SIZE * page_number
    records = graph.cypher.execute('match (p:Person)-[]-(r) with p, r, count(r) as rels where exists(p.person_name_heb) and rels > 0 return r skip {} limit {}'.format(skip, PAGE_SIZE))
    # records = graph.cypher.execute('match (r:Record) return r skip {} limit {}'.format(skip, PAGE_SIZE))
    if not len(records):
        break
    page_number += 1
    for nodes in records:
        for record in nodes:
            record_count += 1
            record_data = eval(record['data'])
            print(str("{}. {}".format(record_count, record_data['control']['recordid'])))
            create_page_from_dictionary(record_data)

print("Done. %s records processed" % record_count)
