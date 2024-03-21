from fastapi import FastAPI
from routerAuth import auth as authenticate
import models
from routerapi import app as results
from database import engine
from starlette.staticfiles import StaticFiles


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
  

app.include_router(authenticate)
app.include_router(results)




