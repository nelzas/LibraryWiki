from requests import get
import xmltodict
import json


def primo_get(document_id):
    """
    Get a record from primo by doximcument id
    :param document_id:
    :return: a json representation of the record
    """
    url = "http://primo.nli.org.il/PrimoWebServices/xservice/search/fullview?institution=NNL&docId=" + document_id + "&json=true"
    top = get(url).json()
    return top['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']


def primo_search(search_term, limit=20):
    """
    Search for a term in primo
    :param search_term: the term to search (can be in hebrew)
    :return: a json representation of the search results
    """
    url = 'http://primo.nli.org.il/PrimoWebServices/xservice/search/brief?institution=NNL&query=any,contains,"' + search_term + '"&indx=1&bulkSize=' + str(
        limit) + '&json=true'
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


class Results:
    _SEARCH_URL = \
        'http://primo.nli.org.il/PrimoWebServices/xservice/search/brief?institution=NNL&query=any,contains,"{}"' \
        '&indx={}&bulkSize={}&json=true'

    def __init__(self, query, count):
        self.count = count
        self.query = query
        self.index = 0
        self.page = 1
        self.results = self._get_results()

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < self.count:
            try:
                res = self.results[self.index]
            except IndexError:
                raise StopIteration
            self.index += 1
            return res
        self.page += 1
        self.index = 0
        self.results = self._get_results()
        return self.__next__()

    def _get_results(self):
        return [item['PrimoNMBib']['record'] for item in self._search()['DOC']]

    def __len__(self):
        return int(self._search()['@TOTALHITS'])

    def _search(self):
        res = get(Results._SEARCH_URL.format(self.query, 1 + (self.page - 1) * self.count, self.count))
        if res.status_code == 500:
            raise StopIteration
        return res.json()['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']
