from database import engine, SessionLocal
from fastapi import Depends,HTTPException
from typing_extensions import Annotated
from models import User
from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from jose import jwt, JWTError
from starlette import status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = '5a9626b0b9d28e876705256960cd14299dc6a37654d8b635c191ab52aafbf6ae'

ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/token")



bcrpyt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(email: str, password: str, db):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    
    if not bcrpyt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(email:str,user_id:int, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        email:str= payload.get('sub')
        user_id:int= payload.get('user_id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication credentials")
        return {"email": email, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    
    