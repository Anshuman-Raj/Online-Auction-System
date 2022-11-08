from http.client import HTTPException
from auth.form import RegisterForm
from db.database import get_db
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse
from db.login import UserCreate, create_new_user

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=True)

@router.get("/register")
def regiter(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    form = RegisterForm(request=request)
    await form.load_data()
    create_new_user_request = UserCreate(
        username=str(form.username),
        email= str(form.email),
        password=str(form.password),
        contact=str(form.contact)
    )
    try:
        user = create_new_user(user=create_new_user_request, db=db)
        form.__dict__.update(msg="Registration Successful :)")
        return RedirectResponse("/login", status_code=307)
    except HTTPException:
        form.__dict__.update(msg="Email already Exists")
        form.errors.append("Email already Exists")
        return templates.TemplateResponse("auth/register.html", form.__dict__)
    except:
        form.__dict__.update(msg="Registration Failed, Email already Exists :(")
        response = templates.TemplateResponse("auth/register.html", form.__dict__)
    return response