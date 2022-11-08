import datetime as _dt
from enum import unique
from operator import truediv
import uuid
import sqlalchemy as _sql
import db.database as _database

# A function to genetate UUID for the primary key for the table user_info
def generate_uuid():
    return str(uuid.uuid4())


class Users(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.String, primary_key=True, index=True, default=generate_uuid)
    username = _sql.Column(_sql.String, index=True, nullable=False, unique=True)
    password = _sql.Column(_sql.String, index=True, nullable=False)
    email = _sql.Column(_sql.String, index=True, nullable=False, unique=True)
    contact = _sql.Column(_sql.String, index=True, nullable=False, unique=True)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

class Auctions(_database.Base):
    __tablename__ = "auctions"
    id = _sql.Column(_sql.String, primary_key=True, index=True, default=generate_uuid)
    auction_name = _sql.Column(_sql.String, index=True, nullable=False)
    start_time = _sql.Column(_sql.DateTime, index=True)
    end_time = _sql.Column(_sql.DateTime, index=True)
    description = _sql.Column(_sql.String, index=True, default="No Description")
    created_by = _sql.Column(_sql.String, _sql.ForeignKey("users.id"), index=True)
    base_bid = _sql.Column(_sql.Integer, index=True, default=0)
    current_bid = _sql.Column(_sql.Integer, index=True, default=0)
    highest_bidder = _sql.Column(_sql.String, index=True, default="No one")