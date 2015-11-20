from app.wiki import create_wiki_page, create_redirect_wiki_page

LIST_ITEM = "* {} : {}\n"
ALEF_LINK = "http://aleph.nli.org.il/F?func=direct&local_base={}&doc_number={}"

def person_name(primo_person_name):
    """
    Convert "last, first, year" to "first last" (year is optional)
    :param name: person name as "last, first, other"
    :return: first last
    """
    splitted = primo_person_name.split(", ",2)
    return splitted[1] + " " + splitted[0]

def create_page_from_dictionary(item_dict):
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
        title = item_dict['sort']['title']
    except:
        title = display['title']
    creator = display['creator']
    creationdate = display.get('creationdate')
    ispartof = display.get('ispartof')
    performed_by = display.get('lds35') # list
    source = display['source']
    lib_link = display['lds21']

    create_redirect_wiki_page(page_name=title, redirect_to=document_id, summary="Creating redirect page for {}".format(document_id))

    content = "{{DISPLAYTITLE:%s}}\n" % title
    content += "'''{}''' נוצר על ידי {}".format(title, creator)
    if (creationdate):
        content += " בשנת {}".format(creationdate)
    content += "\n"
    content += "==פרטים כלליים==\n"
    if (performed_by):
        content += LIST_ITEM.format("שם מבצע", performed_by)
    if (ispartof):
        content += LIST_ITEM.format("מתוך", ispartof)
    content += "==מידע נוסף==\n"
    content += "\n"
    content += LIST_ITEM.format("מקור", source)
    content += "* מספר מערכת: [{} {}]\n".format(lib_link, sourcerecordid)
    content += "== קישורים נוספים ==\n"
    alef_link = ALEF_LINK.format(originalsourceid, sourcerecordid)
    content += "* [{} הפריט בקטלוג הספריה]\n".format(alef_link)

    create_wiki_page(page_name=document_id, summary="Created from primo", content=content)
