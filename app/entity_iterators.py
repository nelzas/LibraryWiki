import re
from time import sleep

from requests import get
import app.authorities
from app.authorities import to_list
import xmltodict
from app.node_entities import Authority, Record, Photo, Portrait
from app.settings import DUMP_PATH

PRIMO = 'primo.nli.org.il'

class Results:
    def __init__(self, query, max_results=200):
        self.count = max_results
        self.query = query
        self.index = 0
        self.page = 1
        self.results = self._get_results()

    @property
    def _search_url(self):
        return 'http://' + PRIMO + '/PrimoWebServices/xservice/search/brief?institution=NNL' \
                                   '&query=any,contains,"{}"&indx={}&bulkSize={}&json=true'

    @property
    def entity_type(self):
        return Record

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < self.count:
            try:
                res = self.results[self.index]
            except IndexError:
                raise StopIteration
            self.index += 1
            return self.entity_type(res)
        self.page += 1
        self.index = 0
        self.results = self._get_results()
        return self.__next__()

    def _get_results(self):
        if self._search().get('DOC'):
            return [item['PrimoNMBib']['record'] for item in to_list(self._search()['DOC']) if
                    item.get('PrimoNMBib') and item['PrimoNMBib'].get('record')]
        return []

    def __len__(self):
        return int(self._search()['@TOTALHITS'])

    def _search(self):
        retries = 0
        while True:
            try:
                res = get(self._search_url.format(self.query, 1 + (self.page - 1) * self.count, self.count))
            except:
                if retries > 10:
                    raise StopIteration
                retries += 1
                print('connection issue...')
                sleep(5)
                continue
            break
        if retries:
            print('all fine!')
        if res.status_code == 500:
            raise StopIteration
        return res.json()['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']
        try:
            return res.json()['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']
        except:
            print('oh.')
            raise StopIteration


class Photos(Results):
    def __init__(self, query, max_results=200):
        super().__init__(query, max_results)

    @property
    def _search_url(self):
        return 'http://primo.nli.org.il/PrimoWebServices/xservice/search/brief?institution=NNL' \
               '&loc=local,scope:(NNL_PIC)&query=facet_topic,exact,"{} M"&sortField=&indx={}&bulkSize={}&json=true'

    @property
    def entity_type(self):
        return Photo


class Portraits(Photos):
    def __init__(self, query):
        super().__init__(query, 2)

    @property
    def _search_url(self):
        return 'http://primo.nli.org.il/PrimoWebServices/xservice/search/brief?institution=NNL' \
               '&loc=local,scope:(NNL01_Schwad)&query=facet_topic,exact,"{} Y M–Portraits"&sortField=&indx={}' \
               '&bulkSize={}&json=true'

    @property
    def entity_type(self):
        return Portrait

def get_authorities(from_id=0, to_id=999999999, list_authorities = []):
    with open(DUMP_PATH) as f:
        buffer = ''
        auth_id = 0
        line = f.readline()
        while not line.strip().endswith('">'):
            line = f.readline()

        for line in f:
            if not auth_id:
                groups = re.match(r'  <controlfield tag="001">(\d*)</controlfield>', line)
                if groups:
                    auth_id = int(groups.group(1))
            buffer += line
            if line.strip() == "</record>":
                if from_id <= auth_id <= to_id and (len(list_authorities) == 0 or auth_id in list_authorities):
                    print(auth_id)
                    record = xmltodict.parse(buffer)['record']
                    result = {k: record[k] for k in record if k == "controlfield" or k == "datafield"}
                    if result.get('datafield'):
                        try:
                            yield Authority(app.authorities.convert_dict(result))
                        except:
                            pass
                elif auth_id > to_id:
                    break
                buffer = ''
                auth_id = 0
