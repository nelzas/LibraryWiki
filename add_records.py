from app.db_comm import set_entities, create_records_authorities_relationships
from app.entity_iterators import Results, Photos

set_entities(Photos('חיים נחמן ביאליק', count=10))
create_records_authorities_relationships()
