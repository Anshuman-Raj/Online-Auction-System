from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from auth.route_login import get_current_user_from_token
from db.auction import create_new_auction, retrieve_auction, retrieve_auctions, update_auction, list_auctions, search_auction, delete_auction, payment_cost
from db.database import get_db
from db.login import get_user_by_email
from db.models import Users
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from webapp.schema import AuctionUpdateRequest, CreateAuctionRequest, BidForm
from datetime import datetime as dt
from fastapi import status
from typing import Optional
from fastapi import HTTPException
from dotenv import load_dotenv
import sqlite3
import razorpay
import os

router = APIRouter(prefix='/auction')
templates = Jinja2Templates(directory="templates")
load_dotenv()
# Homepage for auction
@router.get("/")
def home(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    items = list_auctions(db=db, user=current_user)
    return templates.TemplateResponse("general/homepage.html", {"request": request, "name":current_user.username, "auctions":items, "is_authenticated": "true"})
    
# For creating new auctions
@router.get("/create")
async def create_auction_form(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    return templates.TemplateResponse("auction/create.html", {"request": request, "is_authenticated": "true"})
    

@router.post("/create")
async def create_auction(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    form = CreateAuctionRequest(request)
    await form.load_data()
    if form.end_time > dt.utcnow() and form.start_time < form.end_time and form.start_time > dt.utcnow():
        auction = create_new_auction(id=str(current_user.id),auction=form, db=db)
        return RedirectResponse("/auction", status_code=302)
    else:
        errors = []
        errors.append("Please make sure start time, end time are in future and start time is before end time!")
        return templates.TemplateResponse("auction/create.html", {"request": request, "errors": errors, "is_authenticated": "true"})
    

# Delete Auctions
@router.get("/delete/{id}")
async def delete(id: str, request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    auction = retrieve_auction(id=id, db=db)
    if auction.__dict__["created_by"] == current_user.id:
        delete_auction(id=id, db=db)
        return RedirectResponse(url="/auction/myauctions", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/auction/myauctions", status_code=status.HTTP_400_BAD_REQUEST)


# for getting the details of the the auction
@router.get("/details/{id}")
async def details(id: str, request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    try:
        auction = retrieve_auction(id=id, db=db)
        if auction.__dict__["end_time"] <= dt.utcnow():
            user = get_user_by_email(auction.__dict__["highest_bidder"], db)
            if user is not None:
                username = user.__dict__["username"]
                return templates.TemplateResponse("auction/details.html", {"request": request, "auction": auction, "msg": f"Winner is {username}", "is_authenticated": "true"})
        return templates.TemplateResponse("auction/details.html", {"request": request, "auction": auction, "is_authenticated": "true"})
    except Exception as e:
        print("\n\n")
        print(e,"\n\n")

#  for placing bids on an auction
@router.post("/details/{id}")
async def bid(id:str, request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    auction = retrieve_auction(id=id, db=db)
    form = BidForm(request=request)
    await form.load_data()
    # print("request is: ",request, "\n\n\n") 
    auc = auction.__dict__
    
    # Updating current bid
    upd = AuctionUpdateRequest(
        auction_name=auc["auction_name"],
        start_time=auc["start_time"],
        end_time=auc["end_time"],
        base_bid=auc["base_bid"],
        highest_bidder=str(current_user.email),
        current_bid=form.bid,
        created_by=auc["created_by"],
        description=auc["description"]
    )

    if auc["created_by"] == current_user.id:
        upd.current_bid = auc["current_bid"]
        return templates.TemplateResponse("auction/details.html", {"request": request, "is_authenticated": "true", "auction": upd, "msg": "You cannot bid on your own auctions!"})
    
    if dt.utcnow() > auc["end_time"] or dt.utcnow() < auc["start_time"]:
        print(auc["end_time"], "\n",auc["start_time"],"\n", dt.utcnow(), "\n\n\n")
        upd.current_bid = auc["current_bid"]
        return templates.TemplateResponse("auction/details.html", {"request": request, "is_authenticated": "true", "auction": upd, "msg": "Auction has either ended or has not started yet! Pls check time in UTC"})
    
    is_upd = update_auction(auction_id=id, auction=upd,db=db)
    if is_upd:
        return templates.TemplateResponse("auction/details.html", {"request": request, "is_authenticated": "true", "auction": upd, "msg": "Successfully placed bid!"})
    
    else:
        upd.current_bid = auc["current_bid"]
        return templates.TemplateResponse("auction/details.html", {"request": request, "auction": auction, "msg": "Bid failed, make sure, auction hasn't expired and bid is higher thab base and current bid!"})
   
# My auctions
@router.get("/myauctions")
async def myauctions(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    auctions = retrieve_auctions(db=db, id=str(current_user.id))
    return templates.TemplateResponse("auction/myauction.html", {"request": request, "auctions": auctions, "is_authenticated": "true"})

# autocomplete
@router.get("/autocomplete")
def autocomplete(term: Optional[str] = None, db: Session = Depends(get_db), current_user: Users=Depends(get_current_user_from_token)):
    auctions = search_auction(str(term), db=db)
    auction_names = []
    for auc in auctions:
        auction_names.append(auc.auction_name)
    return auction_names

@router.get("/search/")
def search(
    query: Optional[str], request: Request, db: Session = Depends(get_db), current_user: Users=Depends(get_current_user_from_token)
):
    auctions = search_auction(str(query), db=db)
    return templates.TemplateResponse(
        "general/homepage.html", {"request": request, "auctions": auctions, "is_authenticated": "true"}
    )

@router.get("/pay")
async def get_pay(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    cost = payment_cost(current_user, db)
    try:
        price = int(cost[0])
    except:
        price = 0
    return templates.TemplateResponse("auction/pay_form.html", {"request": request, "is_authenticated": "true", "price":price, "user":current_user})

@router.post("/pay")
async def pay(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    id = str(os.getenv("KEY_ID"))
    secret = str(os.getenv("KEY_SECRET"))
    client = razorpay.Client(auth=(id, secret))
    cost = payment_cost(current_user, db)
    try:
        price = int(cost[0])
    except:
        price = 0
    if price == 0:
        return RedirectResponse(url="/auction/pay", status_code=status.HTTP_302_FOUND)
    amt = price*100
    data = { "amount": amt, "currency": "INR", "receipt": str(current_user.id) }
    payment = client.order.create(data=data)
    
    return templates.TemplateResponse("auction/pay.html", {"request":request, "payment": payment, "amt":amt, "is_authenticated": "true"})