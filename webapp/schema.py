from typing import Optional
from fastapi import Request
from datetime import datetime
from pydantic import BaseModel

class AuctionUpdateRequest(BaseModel):
    auction_name: str
    start_time: datetime
    end_time: datetime
    created_by: str
    description: Optional[str]
    base_bid: Optional[int] = 0
    current_bid: Optional[int] = 0
    highest_bidder: Optional[str]
class CreateAuctionRequest():
    def __init__(self, request: Request):
        self.request: Request = request
        self.auction_name: str
        self.start_time: datetime
        self.end_time: datetime
        self.created_by: str
        self.description: Optional[str]
        self.base_bid: Optional[int] = 0
        self.current_bid: Optional[int] = 0
        self.highest_bidder: Optional[str] =  None
    
    async def load_data(self):
        form = await self.request.form()
        self.auction_name = str(form.get("auction_name"))
        self.start_time = datetime.strptime(str(form.get("start_time")), "%Y-%m-%d %H:%M")
        self.end_time = datetime.strptime(str(form.get("end_time")), "%Y-%m-%d %H:%M")
        self.created_by = str(form.get("created_by"))
        self.description = str(form.get("description"))
        self.base_bid = int(str(form.get("base_bid")))