from app.pages import CR, BR, simple_person_name, date8_to_heb_date
from app.wiki import create_wiki_page, create_redirect_wiki_page
from app.__init__ import *
import json

with open("templates/personality.wiki.template") as f:
    TEMPLATE = f.read()

COLLAPSIBLE = 'class="mw-collapsible mw-collapsed wikitable" width=100%'
LINE_BREAK = '|-' + CR
OPENDIV = '<div style="width: 600px;">'
CLOSEDIV = '</div>'

ITEM = '{{|class="mw-collapsible mw-collapsed wikitable" width=100%' + CR + \
    '!([rosetta.nli.org.il/delivery/DeliveryManagerServlet?dps_pid={rosetta} לצפיה])&nbsp; {title} &nbsp;' + CR + \
    LINE_BREAK + \
    '| הפריט המלא: [[{nnl_prefix}{nnl}|{description}]]' + CR + \
    LINE_BREAK + \
    '|{notes}' + CR + \
    LINE_BREAK + \
    '|תאריך : {date}' + CR + \
    LINE_BREAK + \
    '|[http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId={nnl} הרשומה באתר הספרייה הלאומית ({nnl})]' + CR + \
    '|}}' + CR

template_name = "שם="
template_image_url = "תמונה="
template_birth_date = "תאריך לידה="
template_death_date = "תאריך פטירה="
template_birth_place = "מקום לידה="
template_death_place = "מקום פטירה="
template_address = "מקום מגורים="
template_other_names = "כינויים נוספים="
template_occupation = "מקצוע="

def personality_name(record):
    return record['person_name_heb']

def item(record, tag, code):
    pass

def get_if_exists(dict, *keys):
    dict0 = dict
    try:
        for key in keys:
            dict0 = dict0[key]
        return dict0
    except:
        return ""

def create_page_from_node(person_node, records_list, debug=None, create_category_pages=False):
    """
    Create a person page from a neo4j node
    :param person_node: neo4j node
    :param debug:
    :param create_category_pages:
    :return:
    """
    wiki_page_name = person_node['id']
    person_name = simple_person_name(person_node['person_name_heb'])
    record = json.loads(person_node['data'])

    birth_date = date8_to_heb_date(get_if_exists(record, '046', 0, 'f'))
    death_date = date8_to_heb_date(get_if_exists(record, '046', 0, 'g'))

    birth_place = get_if_exists(record, '370', 0, 'a')
    death_place = get_if_exists(record, '370', 0, 'b')

    other_names = get_if_exists(record, '400')
    other_names_value = BR.join(simple_person_name(other_name['a']) for other_name in other_names)

    address = get_if_exists(record, '371', 0, 'a')
    address_place = get_if_exists(record, '371', 0, 'b')
    address_country = get_if_exists(record, '371', 0, 'd')

    occupation = get_if_exists(record, '374', 0, 'a')
    gender = get_if_exists(record, '375', 0, 'a') # MALE/FEMALE
    female = gender.lower() == "female"

    value_image_url = ""

    content = "{{DISPLAYTITLE:%s}}\n" % person_name

    AUDIO = ["==פריטי שמע==",OPENDIV]
    VIDEO = ["==פריטי וידאו==",OPENDIV]
    BOOKS_BY = ["==ספרים שכתבה==" if female else "==ספרים שכתב==",OPENDIV]
    BOOKS_ABOUT = ["==ספרים אודותיה==" if female else "==ספרים אודותיו==",OPENDIV]
    IMAGES = ["==גלריית תמונות==",OPENDIV]
    OTHER = ["==אחר==",OPENDIV]

    for record_rel in records_list:
        for record_type in records_list[record_rel]:
            for record in records_list[record_rel][record_type]:
                content_item = ITEM.format(**record)
                if record_type == "other":
                    item_type = "other"
                else:
                    item_type = type_dict.get(record_type.lower())[3]
                if item_type == 'print':
                    if record_rel == 'subject_of':
                        BOOKS_ABOUT.append(content_item)
                    else:
                        BOOKS_BY.append(content_item)
                elif item_type == 'audio':
                    AUDIO.append(content_item)
                elif item_type == 'video':
                    VIDEO.append(content_item)
                elif item_type == 'image':
                    if record_rel == 'portrait_of':
                        value_image_url = record['rosetta']
                    else:
                        IMAGES.append(content_item)
                else:
                    OTHER.append(content_item)

    template = TEMPLATE \
        .replace(template_name, template_name + person_name) \
        .replace(template_birth_date, template_birth_date + birth_date) \
        .replace(template_death_date, template_death_date + death_date) \
        .replace(template_birth_place, template_birth_place + birth_place) \
        .replace(template_death_place, template_death_place + death_place) \
        .replace(template_other_names, template_other_names + other_names_value) \
        .replace(template_occupation, template_occupation + occupation) \
        .replace(template_image_url,template_image_url+value_image_url)

    content += template

    notes1 = record.get('670')
    notes2 = record.get('678')
    notes3 = record.get('680')

    notes = []
    for notes_i in (notes1, notes2, notes3):
        if notes_i:
            notes += notes_i

    if notes:
        content += CR
        content += "".join(note['a'] + BR for note in notes)

    content += CR + \
        CR.join(BOOKS_BY) + CLOSEDIV + CR + \
        CR.join(BOOKS_ABOUT) + CLOSEDIV + CR + \
        CR.join(AUDIO) + CLOSEDIV + CR + \
        CR.join(VIDEO) + CLOSEDIV + CR + \
        CR.join(IMAGES) + CLOSEDIV + CR + \
        CR.join(OTHER) + CLOSEDIV + CR

    if debug:
        print(content)
    else:
        redicrect_page_name = "אישיות:" + person_name
        # create_redirect_wiki_page(page_name=redicrect_page_name, redirect_to=wiki_page_name,
        #                           summary="Creating redirect page for {}".format(wiki_page_name))
        create_wiki_page(page_name=wiki_page_name, summary="Created from primo", content=content)

    return content
