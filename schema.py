from pydantic import BaseModel
from typing import Optional
from fastapi import Request


class SignupDetails(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        
    async def create_outh_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")