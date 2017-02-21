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

PUNCTUATION = {',', '.', ':', '!', ';', '?'}
BRACKETS = {'<', '>'}
PUNCTUATION_AND_BRACKETS = PUNCTUATION.copy()
PUNCTUATION_AND_BRACKETS.update(BRACKETS)
PRIMARY = "primary"

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


def handle_person(subfields):
    subfield_a = subfields.get('a') or ""
    subfield_b = subfields.get('b') or ""
    subfield_c = subfields.get('c') or ""
    subfield_d = subfields.get('d') or ""
    lang = subfields['9']
    result = parse_name(subfield_a, subfield_b, subfield_c, lang)
    result.update(absolute_name(subfield_a, subfield_b, subfield_c, subfield_d, lang))
    result.update(handle_subdivision(subfields))
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


def handle_location(subfields):
    result = {"{}_{}".format('location_name', subfields['9']): subfields['a']}
    result.update(handle_subdivision(subfields))
    return result


def handle_corporation(subfields):
    result = {"{}_{}".format('corporation_name', subfields['9']): subfields['a']}
    result.update(handle_subdivision(subfields))
    return result


def handle_topic(subfields):
    result = {"{}_{}".format('topic_name', subfields['9']): subfields['a']}
    result.update(handle_subdivision(subfields))
    return result


def handle_subdivision(subfields):
    """
     Set db fields for authoritiy records with subdivisions (subfields v/x/y/z of name fields(1xx)).
     If no subdivisions then set "primary" to True, otherwise set it to False.
    :param subfields: the entire name group subfields (of a specific language)
    :return:
    """
    result = {}
    result[PRIMARY] = True

    lang = subfields.get('9')

    subfield_form_subdivision = subfields.get('v')
    if subfield_form_subdivision:
        result[PRIMARY] = False
        result["form_subdivision_" + lang] = subfield_form_subdivision

    subfield_general_subdivision = subfields.get('x')
    if subfield_general_subdivision:
        result[PRIMARY] = False
        result["general_subdivision_" + lang] = subfield_general_subdivision

    subfield_chronological_subdivision = subfields.get('y') or ""
    if subfield_chronological_subdivision:
        result[PRIMARY] = False
        result["chronological_subdivision_" + lang] = subfield_chronological_subdivision

    subfield_geographical_subdivision = subfields.get('z') or ""
    if subfield_geographical_subdivision:
        result[PRIMARY] = False
        result["geographical_subdivision_" + lang] = subfield_geographical_subdivision

    return result

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
    '100': handle_person, # person authorities
    '110': handle_corporation, # corporation authorities
    '150': handle_topic, # topic authorities
    '151': handle_location, # location authority
    '046': parse_dates,
    '371': parse_address,
    '374': partial(parse_tag, 'occupation'),
    '375': partial(parse_tag, 'gender'),
    '377': partial(parse_tag, 'language'),
    '681': partial(parse_tag, 'biography'),
}


def to_list(item):
    return item if type(item) is list else [item]


def convert_dict(d, xml_prefix):
    tags = defaultdict(list)
    for tag in d["{xml_prefix}controlfield".format(xml_prefix=xml_prefix)] + \
               d["{xml_prefix}datafield".format(xml_prefix=xml_prefix)]:
        tags[tag['@tag']].append({k: v for k, v in tag.items() if k != '@tag' and k != 'subfield'})
        if not tag.get("{xml_prefix}subfield".format(xml_prefix=xml_prefix)):
            continue
        for sub in to_list(tag["{xml_prefix}subfield".format(xml_prefix=xml_prefix)]):
            tags[tag['@tag']][-1][sub['@code']] = sub['#text']
    return tags
