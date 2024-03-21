from fastapi import FastAPI, APIRouter, Depends,HTTPException,Form,Response
from schema import SignupDetails, Token, LoginForm
from database import SessionLocal
from models import User
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from typing_extensions import Annotated
from datetime import timedelta, datetime
from passlib.context import CryptContext
from sqlalchemy.orm import session
from starlette import status
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        
    async def create_outh_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

auth = APIRouter(prefix="/auth")

templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#db_dependency = Annotated[session, Depends(get_db)]

SECRET_KEY = '5a9626b0b9d28e876705256960cd14299dc6a37654d8b635c191ab52aafbf6ae'

ALGORITHM = "HS256"

oauth2_bearer =  OAuth2PasswordBearer(tokenUrl="/token")
bcrpyt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    if not bcrpyt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])    
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise None
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")


@auth.get("/", response_class=HTMLResponse)
async def authenticationpage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@auth.post("/", response_class=HTMLResponse)
async def login(request:Request, db: session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_outh_form()
        response = RedirectResponse(url="/locale/search", status_code=status.HTTP_302_FOUND)
        
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        
        if not validate_user_cookie:
            msg = "Invalid username or password"
            return templates.TemplateResponse("home.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown error"
        return templates.TemplateResponse("home.html", {"request": request, "msg": msg})




@auth.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@auth.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, db: session = Depends(get_db), email: str = Form(...), username: str = Form(...),
                        first_name: str = Form(...), last_name: str = Form(...), password: str = Form(...), password2: str = Form(...),
                        ):
    
    validation1 = db.query(User).filter(User.username == username).first()
    
    validation2 = db.query(User).filter(User.email == email).first()
    
    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid input"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    
    user_model = User()
    user_model.email = email
    user_model.username = username
    user_model.firstname = first_name
    user_model.lastname = last_name
    user_model.hashed_password = bcrpyt_context.hash(password)    
    db.add(user_model)
    db.commit()
    
    msg = "Register successfully"
    return templates.TemplateResponse("home.html", {"request": request, "msg": msg})










@auth.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        return False
    
    token = create_access_token(user.username, user.id, timedelta(minutes=60))
    
    response.set_cookie(key="access_token", value=token, httponly=True)
    
    return True
