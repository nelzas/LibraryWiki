from app.db_comm import set_entities, create_records_authorities_relationships
from app.entity_iterators import Results

set_entities(Results('NNL_ALEPH'))
create_records_authorities_relationships()
