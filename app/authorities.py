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
import re


def get_authorities(from_id = 0, to_id = 999999999):
    with open('/home/adir/Downloads/nnl10all.xml') as f:
        buffer = ''
        id = 0
        line = f.readline()
        while not line.strip().endswith('">'):
            line = f.readline()

        for line in f:
            if not id:
                groups = re.match(r'  <controlfield tag="001">(\d*)</controlfield>', line)
                if groups:
                    id = int(groups.group(1))
            buffer += line
            if line.strip() == "</record>":
                if id >= from_id and id <= to_id:
                    record = xmltodict.parse(buffer)['record']
                    result = {k: record[k] for k in record if k == "controlfield" or k == "datafield"}
                    yield result
                buffer = ''
                id = 0


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

PUNCTUATION = ",.:!;?"
BRACKETS = "<>"


def remove_all(line, chars_to_remove):
    clean_line = line
    for char in chars_to_remove:
        clean_line = clean_line.replace(char, "")
    return clean_line


def trim_last(line, chars_to_remove):
    clean_line = line
    while clean_line and clean_line[-1] in chars_to_remove:
        clean_line = clean_line[:-1]
    return clean_line


def parse_name(subfields):
    """
    Rules:
    Remove punctuation from end of tag 'a'
    Remove all punctuation from tags 'b' and 'c'
    Remoe all brackets "<" and ">" from all tags
    :param subfields:
    :return: person_name_lang, name where lang is subfield '9'
    """
    subfield_a = subfields.get('a') or ""
    subfield_b = subfields.get('b') or ""
    subfield_c = subfields.get('c') or ""

    subfield_a = trim_last(subfield_a, PUNCTUATION)
    subfield_a = remove_all(subfield_a, BRACKETS)
    subfield_b = remove_all(subfield_b, PUNCTUATION + BRACKETS)
    subfield_c = remove_all(subfield_c, PUNCTUATION + BRACKETS)

    name = subfield_a + (" " if subfield_b else "") + subfield_b + (" " if subfield_c else "") + subfield_c
    lang = subfields['9']
    return "person_name_" + lang, name


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
    if tag == 'person_name':
        return parse_name(subfields)
    if tag == 'location_name':
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
    for tag in d['datafield']:
        if not tag.get('subfield'):
            continue
        tags[tag['@tag']].append({k: v for k, v in tag.items() if k != '@tag' and k != 'subfield'})
        for sub in to_list(tag['subfield']):
            tags[tag['@tag']][-1][sub['@code']] = sub['#text']
    return tags


def db_auth(from_id = 0, to_id = 999999999):
    for record in get_authorities(from_id, to_id):
        if not record.get('datafield'):
            continue
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
