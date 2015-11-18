from requests import get
import xmltodict
import json

def primo_get(document_id):
    """
    Get a record from primo by document id
    :param document_id:
    :return: a json representation of the record
    """
    url = "http://primo.nli.org.il/PrimoWebServices/xservice/search/fullview?institution=NNL&docId=" + document_id + "&json=true"
    top = get(url).json()
    return top['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']

def primo_search(search_term):
    """
    Search for a term in primo
    :param search_term: the term to search (can be in hebrew)
    :return: a json representation of the search results
    """
    url = 'http://primo.nli.org.il/PrimoWebServices/xservice/search/brief?institution=NNL&query=any,contains,"' + search_term + '"&indx=1&bulkSize=20&json=true'
    top = get(url).json()
    return top['sear:SEGMENTS']['sear:JAGROOT']['sear:RESULT']

def file_get(file_name):
    """
    For debug purposes
    :param file_name: an XML file with 'record' tag as root
    :return: json representation of the file
    """
    f = open(file_name, "r").read()
    return json.dumps(xmltodict.parse(f)['record'])
