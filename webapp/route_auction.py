from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from auth.route_login import get_current_user_from_token
from db.auction import create_new_auction, retrieve_auction, retrieve_auctions, update_auction
from db.database import get_db
from db.login import get_user_by_email
from db.models import Users
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from webapp.schema import AuctionUpdateRequest, CreateAuctionRequest
from datetime import datetime as dt

router = APIRouter(prefix='/auction')
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(request: Request, current_user: Users = Depends(get_current_user_from_token)):
    return templates.TemplateResponse("general/homepage.html", {"request": request, "name":current_user.username})


@router.post("/create")
async def create_auction(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    form = CreateAuctionRequest(request)
    await form.load_data()
    auction = await create_new_auction(email=str(current_user.email),auction=form, db=db)
    return auction

#  for placing bids on an auction
@router.post("/details/{id}")
async def bid(id:str, request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    auction = retrieve_auction(id=id, db=db)
     
    auc = auction.__dict__
    
    upd = AuctionUpdateRequest(
        auction_name=auc["auction_name"],
        start_time=auc["start_time"],
        end_time=auc["end_time"],
        base_bid=auc["base_bid"],
        highest_bidder=str(current_user.email),
        current_bid=int(str(request.get("bid"))),
        created_by=auc["created_by"],
        description=auc["description"]
    )
    if dt.utcnow() > auc["end_time"] or dt.utcnow() < auc["start_time"]:
        upd.current_bid = auc["current_bid"]
        return RedirectResponse(f"/details/{id}")

    is_upd = update_auction(auction_id=id, auction=upd,db=db,bid=request.get(bid),email=current_user.id)
    if is_upd:
        return templates.TemplateResponse("auction/details.html", {"request": request, "auction": upd, "msg": "Successfully placed bid!"})
    
    else:
        upd.current_bid = auc["current_bid"]
        return RedirectResponse(f"/details/{id}")

# for getting the details of the the auction
router.get("/details/{id}")
async def details(id: str, request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    auction = retrieve_auction(id=id, db=db)
    if auction.__dict__["end_time"] <= dt.utcnow():
        user = get_user_by_email(auction.__dict__["highest_bidder"], db)
        return templates.TemplateResponse("auction/details.html", {"request": request, "auction": auction, "msg": f"Winner is {user}"})

    return templates.TemplateResponse("auction/details.html", {"request": request, "auction": auction})

# My auctions
router.post("/myauctions")
async def myauctions(request: Request, current_user: Users = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    auctions = retrieve_auctions(db=db, email=str(current_user.email))
    return templates.TemplateResponse("auction/myauction.html", {"request": request, "auctions": auctions})

# My profile

# logout??