from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import asyncio
from datetime import datetime, timedelta

from app.buyer_agent import BuyerAgent

# Create the FastAPI instance right away
app = FastAPI()

# Session storage with expiration
sessions = {}

class NegotiationInput(BaseModel):
    product: str
    budget: int
    seller_message: str
    session_id: str | None = None 

class ResetInput(BaseModel):
    session_id: str

@app.on_event("startup")
async def startup_event():
    async def cleanup_sessions():
        while True:
            now = datetime.now()
            expired = [sid for sid, session in sessions.items() 
                       if now - session['last_active'] > timedelta(hours=1)]
            for sid in expired:
                del sessions[sid]
            await asyncio.sleep(3600)
    
    asyncio.create_task(cleanup_sessions())

@app.post("/api/negotiate")
async def negotiate(input_data: NegotiationInput):
    try:
        if input_data.budget <= 0:
            raise HTTPException(status_code=400, detail="Budget must be a positive number.")
        
        try:
            seller_offer = int(input_data.seller_message)
            if seller_offer <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Seller offer must be a positive number.")

        sid = input_data.session_id or str(uuid.uuid4())

        if sid not in sessions:
            sessions[sid] = {
                'agent': BuyerAgent(product=input_data.product, budget=input_data.budget),
                'last_active': datetime.now()
            }
        
        session = sessions[sid]
        session['last_active'] = datetime.now()
        
        response = session['agent'].negotiate(seller_offer)
        
        return JSONResponse({
            "session_id": sid,
            "response": {
                "action": response.action,
                "message": response.message,
                "offer_price": response.offer_price
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset(input_data: ResetInput):
    if input_data.session_id in sessions:
        del sessions[input_data.session_id]
    return {"status": "reset"}

# Mount static files *after* API routes to ensure routes are prioritized
app.mount("/", StaticFiles(directory="static", html=True), name="static")
