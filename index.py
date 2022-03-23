# Local Imports
import asyncio
import motor.motor_asyncio

from typing import Optional

# FastAPI
import uvicorn

from fastapi import FastAPI

from fastapi import Request, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.responses import ORJSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.openapi.utils import get_openapi

# Other Imports
import cool_utils

app = FastAPI(
	version="0.0.0.1"
)
cool_utils.JSON.open("./config.json")

BASE = "https://dash.senarc.org"
MONGO = cool_utils.JSON.get("MONGO")

templates = Jinja2Templates(directory="templates")
cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGO)
cluster.get_io_loop = asyncio.get_running_loop
pb = cluster["senarc"]["admin"]

@app.get("/")
async def home(request: Request, account: Optional[str] = Cookie(None)):
	if account is None:
		return BASE + "/login"
	
	if await pb.find_one({"username": account['username']}) is None:
		return BASE + "/login?error=invalid_account"
		return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(request: Request, error: Optional[str] = None):
	if error == "invalid_account":
		return templates.TemplateResponse("login.html", {"status": "invalid"})

	elif error == "500":
		return templates.TemplateResponse("login.html", {"status": "500"})

	else:
		return templates.TemplateResponse("login.html", {"status": "online"})

@app.get("/validate")
async def validate_account(request: Request, username: str, password: str):
	if pb.count_documents({'username': username, 'password': password}) == 0:
		return BASE + "/login?error=invalid_account"

if __name__ == '__main__':
    uvicorn.run("main:app",host='127.0.0.1', port=2201, reload=True, debug=True, workers=2)