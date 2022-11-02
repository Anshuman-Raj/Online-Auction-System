from fastapi import HTTPException
from db.models import Users, Auctions
from webapp.schema import AuctionUpdateRequest, CreateAuctionRequest
from sqlalchemy.orm import Session
from db.login import get_user_by_email
import bcrypt
from pydantic import BaseModel
from datetime import datetime as dt


def create_new_auction(email:str, auction: CreateAuctionRequest, db: Session):
    is_present = get_user_by_email(email, db)
    if is_present is not None:
        raise HTTPException(status_code=409, detail='Email already registered')
    auc = Auctions(
        auction_name = auction.auction_name,
        start_time = auction.start_time,
        end_time = auction.end_time,
        description = auction.description,
        created_by = email,
        base_bid = auction.base_bid,
        current_bid = auction.current_bid,
    )
    db.add(auc)
    db.commit()
    db.refresh(auc)
    return auc

def retrieve_auction(id: str, db: Session):
    item = db.query(Auctions).filter(Auctions.id == id).first()
    return item


def retrieve_auctions(email: str, db: Session):
    items = db.query(Auctions).filter(Auctions.created_by == email)
    return items

def list_auctions(db: Session):
    items = db.query(Auctions).filter(Auctions.end_time > dt.utcnow())
    return items

def update_auction(auction_id: str, auction: AuctionUpdateRequest, db: Session, bid, email):
    existing_auction = db.query(Auctions).filter(Auctions.id == auction_id)
    if not existing_auction.first():
        return 0
    if bid>existing_auction.__dict__["current_bid"]:
        auction.__dict__.update(
            current_bid = bid,
            highest_bidder = email
        )  # update dictionary with new  value of current_bid
    else:
        return 0
    existing_auction.update(auction.__dict__)
    db.commit()
    return 1