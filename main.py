import os
from fastapi import APIRouter, FastAPI, Request
from fastapi_login import LoginManager
from auth import config
from auth.route_login import router as r1
from auth.login import router as r2
from auth.register import router as r3
from webapp.route_auction import router as r4
from fastapi.staticfiles import StaticFiles
import uvicorn
from db.services import _add_tables


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


router = APIRouter(prefix='/login')
router.include_router(r1)

app = FastAPI()

app.include_router(router)
app.include_router(r2)
app.include_router(r3)
app.include_router(r4)
_add_tables()
configure_static(app)
if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)