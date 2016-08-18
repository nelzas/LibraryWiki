import json
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
        # assign id + dumps the entire xml record in 'data' field
        properties = {'data': json.dumps(self.data), 'id': self.data['001'][0]['#text']}
        # assigns type
        if '100' in self.data:
            properties['type'] = 'Person'
        elif '151' in self.data:
            properties['type'] = 'Location'
        elif '150' in self.data:
            properties['type'] = 'Topic '
        else:
            properties['type'] = None
        for tag, subfields in self.data.items():
            for subfield in subfields:
                CODES.get(tag) and properties.update(CODES[tag](subfield))

        return properties

    def _build_labels(self):
        authority_type = self.properties['type']
        if authority_type:
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
        self.data = data
        self._fl_url = "http://aleph.nli.org.il/X?op=find-doc&doc_num={}&base={}"
        self._fl_url = self._build_fl_url()
        super().__init__(data)

    @property
    def _fl_base(self):
        return 'nnl03'

    def _build_fl_url(self):
        return self._fl_url.format(self.data['control']['sourcerecordid'], self._fl_base)

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
        fields = xmltodict.parse(get(self._fl_url).content)['find-doc'].get('record')
        if not fields:
            return None
        fields = fields['metadata']['oai_marc']['varfield']
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
