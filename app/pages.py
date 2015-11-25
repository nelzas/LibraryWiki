from app.wiki import create_wiki_page, create_redirect_wiki_page
from app.__init__ import *
import re

LIST_ITEM = "* {} : {}\n"
ALEF_LINK = "http://aleph.nli.org.il/F?func=direct&local_base={}&doc_number={}"
WIKI_LINK = "[[{}|{}]]" # first the link then the display text
AUTHORITY_ID_PATTERN = ".*\$\$E(.*)\$\$I(.*)\$\$P" # e.g. "$$Dרכטר, יוני, 1951-$$Eרכטר, יוני, 1951-$$INNL10000110663$$PY M"

def str_to_list(str_or_list):
    if type(str_or_list) is str:
        return [str_or_list]
    else:
        return str_or_list

def comma_and(line):
    return ' ו'.join(line.rsplit(', ', maxsplit=1))

def entries_to_authority_id(browse_entries):
    authority_dictionary = {}
    for author in browse_entries:
        match = re.search(AUTHORITY_ID_PATTERN, author)
        if match:
            authority_dictionary[match.group(1)] = match.group(2)[5:]
    return authority_dictionary

def person_name(persons_to_id, primo_person_name):
    """
    Convert "last, first, year" to "first last" (year is optional)
    :param name: person name as "last, first, other"
    :return: first last
    """
    link = persons_to_id.get(primo_person_name)
    if not link:
        person_name_no_role = primo_person_name[:primo_person_name.rfind(" ")]
        link = persons_to_id.get(person_name_no_role)
    splitted = primo_person_name.split(", ",2)
    display_name = splitted[1] + " " + splitted[0]
    if link:
        return WIKI_LINK.format(link, display_name)
    else:
        return display_name

def trim(line):
    """
    Trim non-alpha characters from the end of the line. Leave parentheses.
    For example trime("abc def..") returns "abc def"
    :param line: a string
    :return: the same string without trailing non-alpha characters
    """
    clean_line = line
    while clean_line and not clean_line[-1].isalnum() and not clean_line[-1] == ")":
        clean_line = clean_line[:-1]
    return clean_line

def create_page_from_dictionary(item_dict, debug=None):
    """
    create a wikipedia page from a dictionary that describes a primo item
    :param item_dict: primo item as a dictionary/json
    :return:
    """
    document_id = item_dict['control']['recordid']
    sourcerecordid = item_dict['control']['sourcerecordid']
    originalsourceid = item_dict['control']['originalsourceid']
    display = item_dict['display']
    try:
        title = trim(item_dict['sort']['title'])
    except:
        title = display['title']
    item_type = display['type']

    try:
        display_type = type_dict[item_type][1] # hebrew type as a definite article, e.g. כתב העת
        display_type += " "
    except Exception as e:
        display_type = ""
        print("Unrecognized type '{}'".format(item_type))

    creation_verb = type_dict[item_type][2]
    creators_field = display.get('creator')
    creator = None
    if creators_field:
        authors_to_id = entries_to_authority_id(str_to_list(item_dict['browse']['author']))
        creators = creators_field.split(";")
        creator = ", ".join(set([person_name(authors_to_id, creator.strip()) for creator in creators]))
        creator = comma_and(creator)

    creationdate = display.get('creationdate')
    ispartof = display.get('ispartof')
    performed_by = display.get('lds35') # list
    performed_by = str_to_list(performed_by)

    performed_by_str = None
    if performed_by:
        performed_by_str = ", ".join(person_name(authors_to_id, performer) for performer in performed_by)

    source = display['source']
    lib_link = display['lds21']

    content = "{{DISPLAYTITLE:%s}}\n" % title
    content += "{}'''{}''' {} על ידי {}".format(display_type, title, creation_verb, creator)
    if (creationdate):
        content += " בשנת {}".format(creationdate)
    content += "\n"
    content += "==פרטים כלליים==\n"
    if (performed_by_str):
        content += LIST_ITEM.format("שם מבצע", performed_by_str)
    if (ispartof):
        content += LIST_ITEM.format("מתוך", ispartof)
    content += "==מידע נוסף==\n"
    content += "\n"
    content += LIST_ITEM.format("מקור", source)
    content += "* מספר מערכת: [{} {}]\n".format(lib_link, sourcerecordid)
    content += "== קישורים נוספים ==\n"
    alef_link = ALEF_LINK.format(originalsourceid, sourcerecordid)
    content += "* [{} הפריט בקטלוג הספריה]\n".format(alef_link)

    if not debug:
        create_redirect_wiki_page(page_name=title, redirect_to=document_id, summary="Creating redirect page for {}".format(document_id))
        create_wiki_page(page_name=document_id, summary="Created from primo", content=content)

    return content