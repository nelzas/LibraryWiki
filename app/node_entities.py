import json
import app.authorities
from app import entity_iterators
from app.authorities import CODES
from requests import get
import xmltodict


class Entity:
    def __init__(self, data):
        self.data = data
        self.properties = self._build_properties()
        self.labels = self._build_labels()

    def _build_properties(self):
        raise NotImplemented

    def _build_labels(self):
        raise NotImplemented


class Authority(Entity):
    def _build_properties(self):
        self.properties['data'] = json.dumps(self.data)
        self.properties['id'] = self.data['001'][0]['#text']
        for tag, subfields in self.data.items():
            CODES[tag] and self.properties.update(CODES[tag](subfields[0]))
        if '100' in self.data:
            self.properties['type'] = 'person'
        elif '151' in self.data:
            self.properties['type'] = 'location'

    def _build_labels(self):
        authority_type = self.properties['type']
        if type:
            return 'Authority', authority_type
        return 'Authority',


class Record(Entity):
    def _build_properties(self):
        return {'id': self.data['control']['recordid'], 'data': str(self.data),
                'title': self.data['display']['title']}

    def _build_labels(self):
        return 'Record', self.data['display']['type']


class Photo(Record):
    def __init__(self, data):
        self._fl_url = "http://aleph.nli.org.il/X?op=find-doc&doc_num={}&base={}"
        self._fl_url = self._build_fl_url()
        super().__init__(data)

    @property
    def _fl_base(self):
        return 'nnl03'

    def _build_fl_url(self):
        return self._fl_url.format(self.properties['control']['sourcerecordid'], self._fl_base)

    def _build_properties(self):
        properties = super()._build_properties()
        fl = self._get_fl()
        if fl:
            properties["fl"] = fl
        return properties

    def _build_labels(self):
        return super()._build_labels() + ('Photo',)

    def _get_fl(self):
        fl = None
        fields = xmltodict.parse(get(self._fl_url).content)['find-doc']['record']['metadata']['oai_marc']['varfield']
        for field in fields:
            if not isinstance(field, dict) or not field.get('@id'):
                continue
            if field['@id'] == 'ROS':
                fl = [sub['#text'] for sub in field['subfield'] if sub.get('@label') == 'd'] or None
                break
        return fl and fl[0]


class Portrait(Photo):
    def _build_properties(self):
        properties = super()._build_properties()
        topic = self.data['facets'].get('topic')
        if topic:
            properties['topic'] = topic
        return properties

    @property
    def _fl_base(self):
        return 'nnl01'

    def _build_labels(self):
        return super()._build_labels() + ('Portrait',)


def db_auth():
    for record in entity_iterators.get_authorities():
        if not record.get('datafield'):
            continue
        properties = {'id': record['controlfield'][2]['#text'],
                      'data': json.dumps(app.authorities.convert_dict(record))}
        if record.get('datafield'):
            dat = app.authorities.to_list(record['datafield'])
            tags = [app.authorities.CODES.get(data['@tag']) or data['@tag'] for data in dat]
            if app.authorities.CODES['100'] in tags:
                properties['type'] = 'person'
            elif app.authorities.CODES['151'] in tags:
                properties['type'] = 'location'
            else:
                pass
            if tags and dat[0].get('subfield'):
                for i, tag in enumerate(tags):
                    subfields = {sub['@code']: sub['#text'] for sub in app.authorities.to_list(dat[i].get('subfield'))}
                    info = app.authorities.parse_tag(tags[i], subfields)
                    if info:
                        properties[info[0]] = info[1]
                yield properties
