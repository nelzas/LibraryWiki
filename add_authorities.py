from app.db_comm import set_entities, set_portraits, set_photos
from app.entity_iterators import get_authorities

set_entities(get_authorities())
set_portraits()
set_photos()
