from fastapi import HTTPException
from db.models import Users, Auctions
from webapp.schema import AuctionUpdateRequest, CreateAuctionRequest
from sqlalchemy.orm import Session
from db.login import get_user_by_email
import bcrypt
from pydantic import BaseModel
from datetime import datetime as dt


def create_new_auction(id:str, auction: CreateAuctionRequest, db: Session):
    # is_present = get_user_by_email(email, db)
    # if is_present is not None:
    #     raise HTTPException(status_code=409, detail='Email already registered')
    auc = Auctions(
        auction_name = auction.auction_name,
        start_time = auction.start_time,
        end_time = auction.end_time,
        description = auction.description,
        created_by = id,
        base_bid = auction.base_bid,
        current_bid = auction.current_bid,
    )
    print("\n\n\n", auc.__dict__)
    db.add(auc)
    db.commit()
    db.refresh(auc)
    return auc

def retrieve_auction(id: str, db: Session):
    item = db.query(Auctions).filter(Auctions.id == id).first()
    return item


def retrieve_auctions(id: str, db: Session):
    items = db.query(Auctions).filter(Auctions.created_by == id)
    return items

def list_auctions(user: Users, db: Session):
    items = db.query(Auctions).filter(Auctions.end_time > dt.utcnow(), Auctions.created_by != user.id)
    return items

def update_auction(auction_id: str, auction: AuctionUpdateRequest, db: Session):
    existing_auction = retrieve_auction(id = auction_id, db=db)
    e_auc =db.query(Auctions).filter(Auctions.id == auction_id)
    eauc = existing_auction.__dict__
    print(eauc, "\n\n\n")
    if existing_auction is None:
        return 0
    if auction.current_bid>eauc["current_bid"] and auction.current_bid>eauc["base_bid"]:
        e_auc.update(auction.__dict__)
    else:
        return 0
    db.commit()
    return 1

def search_auction(query: str, db: Session):
    items = db.query(Auctions).filter(Auctions.auction_name.contains(query))
    return items


def delete_auction(id: str, db: Session):
    item = db.query(Auctions).filter(Auctions.id == id)
    item.delete()
    db.commit()