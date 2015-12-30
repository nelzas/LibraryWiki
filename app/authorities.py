# d = {'100': 'person_name',
#      '151': 'location_name',
#      '400': 'alternate_person_name',
#      '451': 'alternate_location_name',
#      '046': 'life_span',
#      '370': 'birth_death_places',
#      '371': 'address',
#      '372': 'related_term',
#      '373': 'related_term',
#      '376': 'related_term',
#      '378': 'related_term',
#      '374': 'occupation',
#      '375': 'gender',
#      '377': 'language',
#      '500': 'relationship',
#      '510': 'relationship',
#      '550': 'relationship',
#      '670': 'notes',
#      '678': 'notes',
#      '680': 'notes',
#      '681': 'biography',
#      }
from collections import defaultdict

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


codes = {
    '100': 'person_name',
    '151': 'location_name',
    '046': 'life_span',
    '371': 'address',
    '374': 'occupation',
    '375': 'gender',
    '377': 'language',
    '681': 'biography',
}


def parse_lang(tag, subfields):
    return "{}_{}".format(tag, subfields['9']), subfields['a']


def parse_dates(subfields):
    dates = []
    context = ('from ', 'until ')
    state = 0
    if subfields.get('s'):
        dates.append(subfields.get('s'))
    if subfields.get('t'):
        dates.append(subfields.get('t'))
        state = 1
    if subfields.get('f'):
        dates.append(subfields.get('f'))
    if subfields.get('g'):
        dates.append(subfields.get('g'))
        state = 1
    if len(dates) == 1:
        return context[state] + dates[0]
    return dates[0] + "-" + dates[1]


def parse_address(subfields):
    first = True

    def no_none(param):
        nonlocal first
        addr = subfields.get(param) or ''
        if first:
            if addr:
                first = False
            return addr
        if addr:
            return ', ' + addr
        return addr

    return no_none('a') + no_none('b') + no_none('c')


def parse_tag(tag, subfields):
    if tag == 'person_name' or tag == 'location_name':
        return parse_lang(tag, subfields)
    if tag == 'life_span':
        return tag, parse_dates(subfields)
    if tag == 'address':
        return tag, parse_address(subfields)
    if tag == 'occupation' or tag == 'gender' or tag == 'language' or tag == 'biography':
        return tag, subfields['a']


def to_list(item):
    return item if type(item) is list else [item] or []


def conv_dict(d):
    tags = defaultdict(list)
    if not d.get('datafield'):
        return None

    for tag in d['datafield']:
        if not tag.get('subfield'):
            continue
        tags[tag['@tag']].append({k: v for k, v in tag.items() if k != '@tag' and k != 'subfield'})
        for sub in to_list(tag['subfield']):
            tags[tag['@tag']][-1][sub['@code']] = sub['#text']
    return tags


def db_auth():
    for record in get_authorities():
        properties = {'id': record['controlfield'][2]['#text'], 'data': json.dumps(conv_dict(record))}
        if record.get('datafield'):
            dat = to_list(record['datafield'])
            tags = [codes.get(data['@tag']) or data['@tag'] for data in dat]
            if codes['100'] in tags:
                properties['type'] = 'person'
            elif codes['151'] in tags:
                properties['type'] = 'location'
            else:
                pass
            if tags and dat[0].get('subfield'):
                for i, tag in enumerate(tags):
                    subfields = {sub['@code']: sub['#text'] for sub in to_list(dat[i].get('subfield'))}
                    info = parse_tag(tags[i], subfields)
                    if info:
                        properties[info[0]] = info[1]
                yield properties
