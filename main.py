from fastapi import APIRouter, FastAPI
from auth import config
from auth.route_login import router as r1
from auth.login import router as r2
from auth.register import router as r3
from fastapi.staticfiles import StaticFiles
import uvicorn


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


router = APIRouter(prefix='/login')
router.include_router(r1)

app = FastAPI()
app.include_router(router)
app.include_router(r2)
app.include_router(r3)

configure_static(app)
if __name__ == "__main__":
    uvicorn.run(app=app)