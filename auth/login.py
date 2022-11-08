from auth.route_login import login_for_access_token
from db.database import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import status
from sqlalchemy.orm import Session
from auth.form import LoginForm


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=True)

@router.get("/")
def log_redirect(request: Request):
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    
@router.get("/login")
def login_(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = templates.TemplateResponse("auth/login.html", form.__dict__)
            login_for_access_token(response=response, form_data=form, db=db)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.errors.append("Incorrect Email or Password")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
        except ValueError:
            form.__dict__.update(msg="")
            form.errors.append("Incorrect Password")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
    return templates.TemplateResponse("auth/login.html", form.__dict__)

# logout
@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse('/login', status_code= 302)
    response.delete_cookie(key ='access_token')
    return response