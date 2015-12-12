import xmltodict
import json


def get_authorities():
    with open('/home/adir/Downloads/nnl10all.xml') as f:
        buffer = ''
        line = f.readline()
        while not line.strip().endswith('">'):
            line = f.readline()

        for line in f:
            buffer += line
            if line.strip() == "</record>":
                record = xmltodict.parse(buffer)['record']
                result = {k: record[k] for k in record if k == "controlfield" or k == "datafield"}
                yield result
                buffer = ''


for record, _ in zip(get_authorities(), range(50)):
    # print(data for data in record['datafield'] if data['@tag'] == 100 and )
    print(record['datafield'][0]['subfield'])
    # print(code for code in )
exit()
for record, _ in zip(get_authorities(), range(50)):
    tags = [data['@tag'] for data in record['datafield']]
    if '100' in tags:
        print("person id: " + record['controlfield'][2]['#text'])
    elif '151' in tags:
        print("location id: " + record['controlfield'][2]['#text'])
