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
from functools import partial

import xmltodict
import re


PUNCTUATION = {',', '.', ':', '!', ';', '?'}
BRACKETS = {'<', '>'}
PUNCTUATION_AND_BRACKETS = PUNCTUATION.copy().update(BRACKETS)


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


def handle_names(subfields):
    subfield_a = subfields.get('a') or ""
    subfield_b = subfields.get('b') or ""
    subfield_c = subfields.get('c') or ""
    subfield_d = subfields.get('d') or ""
    lang = subfields['9']
    result = parse_name(subfield_a, subfield_b, subfield_c, lang)
    result.update(absolute_name(subfield_a, subfield_b, subfield_c, subfield_d, lang))
    return result


def parse_name(subfield_a, subfield_b, subfield_c, lang):
    """
    Rules:
    Remove punctuation from end of tag 'a'
    Remove all punctuation from tags 'b' and 'c'
    Remoe all brackets "<" and ">" from all tags
    :param subfield_a
    :param subfield_b
    :param subfield_c
    :param lang
    :return: person_name_lang, name where lang is subfield '9'
    """

    subfield_a_processed = trim_last(subfield_a, PUNCTUATION)
    subfield_a_processed = remove_all(subfield_a_processed, BRACKETS)
    subfield_b_processed = remove_all(subfield_b, PUNCTUATION_AND_BRACKETS)
    subfield_c_processed = remove_all(subfield_c, PUNCTUATION_AND_BRACKETS)

    name = subfield_a_processed + (" " if subfield_b_processed else "") + subfield_b_processed + (
        " " if subfield_c_processed else "") + subfield_c_processed
    return {"person_name_" + lang: name.strip()}


def absolute_name(subfield_a, subfield_b, subfield_c, subfield_d, lang):
    if lang != 'lat':
        return {}
    absolute = subfield_a + (" " if subfield_b else "") + subfield_b + (" " if subfield_c else "") + subfield_c + (
        " " if subfield_d else "") + subfield_d
    return {"person_name_absolute": absolute.strip()}


def parse_lang(subfields):
    return {"{}_{}".format('location_name', subfields['9']): subfields['a']}


def parse_dates(subfields):
    dates = [None, None]
    contexts = ('from', 'until')
    dates[0] = subfields.get('s') or subfields.get('f')
    dates[1] = subfields.get('t') or subfields.get('g')
    return {context: date for context, date in zip(contexts, dates) if date}


def parse_address(subfields):
    first = True

    def no_none(param):
        nonlocal first
        address = subfields.get(param) or ''
        if first:
            if address:
                first = False
            return address
        if address:
            return ', ' + address
        return address

    return {'address': no_none('a') + no_none('b') + no_none('c')}


def parse_tag(tag, subfields):
    return {tag: subfields['a']}


CODES = {
    '100': handle_names,
    '151': parse_lang,
    '046': parse_dates,
    '371': parse_address,
    '374': partial(parse_tag, 'occupation'),
    '375': partial(parse_tag, 'gender'),
    '377': partial(parse_tag, 'language'),
    '681': partial(parse_tag, 'biography'),
}


def to_list(item):
    return item if type(item) is list else [item]


def convert_dict(d):
    tags = defaultdict(list)
    for tag in d['datafield'] + d['controlfield']:
        tags[tag['@tag']].append({k: v for k, v in tag.items() if k != '@tag' and k != 'subfield'})
        if not tag.get('subfield'):
            continue
        for sub in to_list(tag['subfield']):
            tags[tag['@tag']][-1][sub['@code']] = sub['#text']
    return tags
