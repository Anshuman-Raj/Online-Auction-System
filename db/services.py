import db.database as _database
import models 

def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)

_add_tables()