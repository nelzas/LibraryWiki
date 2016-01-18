from app.db_comm import set_entities, create_records_authorities_relationships
from app.entity_iterators import Results, Photos

set_entities(Photos('גולדה מאיר', count=10))
print('bam')
create_records_authorities_relationships()
