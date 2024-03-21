from fastapi import APIRouter,Depends,HTTPException,FastAPI,status,Form
from typing_extensions import Annotated
from sqlalchemy.orm import Session,session
from routerAuth import get_db, get_current_user
from models import User, Region,State,LGA
from pathlib import Path
from functools import lru_cache
import redis.asyncio as redis
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi_simple_rate_limiter import rate_limiter
from starlette.responses import RedirectResponse
from typing import List, Optional


app = APIRouter(prefix="/locale")


templates = Jinja2Templates(directory='templates')

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/search",response_class=HTMLResponse)
async def read_regions_and_search_for_state(request: Request,user:user_dependency):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("search.html", {"request": request})

@lru_cache(maxsize=3)
@app.post("/search/region",response_class=HTMLResponse)
@rate_limiter(limit=50, seconds=300)
async def read_regions_and_search_for_state(request: Request,user:user_dependency,db:db_dependency, region: str=Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)
    print(region)
    if region == "All states":
        all_states = db.query(State, Region).join(Region).all()
    else:
        all_states= db.query(State,Region).join(Region).filter(Region.name==region).all()
        
    data =[]
    for state, region in all_states:
        state_info = {
            "name": state.name,
            "state_capital": state.state_capital,
            "region_name": region.name
        }
        data.append(state_info)
    return templates.TemplateResponse("state_by_region.html",{"request":request,"data":data})



@app.post("/search/state",response_class=HTMLResponse)
@rate_limiter(limit=50, seconds=300)
async def lgas_for_state(request: Request,user:user_dependency,db:db_dependency,statename:str=Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)
    all_lgas_by_state = db.query(LGA,State).join(State).filter(State.name == statename).all()
    data = []
    for lga in all_lgas_by_state:
        one_lga = lga.LGA.name
        data.append(one_lga)

    return templates.TemplateResponse("lga_by_state.html",{"request":request,"data":data,"statename":statename})




