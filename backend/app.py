"""
=========================================================
Meeple Cafe AI Ordering Chatbot
FastAPI Backend
Version : 4.0.0
Gemini + FAISS Edition
Author  : Sugumar R
=========================================================
"""

from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    ALLOWED_ORIGINS,
    RESTAURANT_NAME,
    RESTAURANT_PHONE,
    RESTAURANT_EMAIL,
    OPENING_HOURS,
)

from backend.chatbot import CafeChatbot
from backend.search_engine import SearchEngine
from backend.ordering import OrderManager
from backend.rag import rag_engine
from backend.memory import memory
from backend.utils import (
    current_datetime,
    health_status,
    success_response,
)

# ==========================================================
# Lazy-loaded Services
# ==========================================================

chatbot = None
search_engine = None
order_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot, search_engine, order_manager

    print("=" * 60)
    print("🚀 Starting Meeple Cafe AI Ordering Chatbot v4")
    print("=" * 60)

    try:
        chatbot = CafeChatbot()
        search_engine = SearchEngine()
        order_manager = OrderManager()

        print("✅ Chatbot Loaded")
        print("✅ Search Engine Loaded")
        print("✅ Order Manager Loaded")
        print("✅ RAG Engine Loaded")
        print("✅ Conversation Memory Loaded")

    except Exception as e:
        print(f"❌ Startup Error: {e}")

    yield

    print("=" * 60)
    print("🛑 Application Shutdown")
    print("=" * 60)


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Models
# ==========================================================

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


class OrderItem(BaseModel):
    id: int
    quantity: int


class OrderRequest(BaseModel):
    customer_name: str
    phone: str
    email: Optional[str] = None
    address: str
    payment_method: str
    items: List[OrderItem]


class HealthResponse(BaseModel):
    status: str
    version: str
    server_time: str


class InfoResponse(BaseModel):
    application: str
    version: str
    restaurant: str
    status: str


@app.get("/")
def home():
    return {
        "application": API_TITLE,
        "version": API_VERSION,
        "status": "Running",
        "restaurant": RESTAURANT_NAME,
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status=health_status(),
        version=API_VERSION,
        server_time=current_datetime(),
    )


@app.get("/info", response_model=InfoResponse)
def info():
    return InfoResponse(
        application=API_TITLE,
        version=API_VERSION,
        restaurant=RESTAURANT_NAME,
        status="Running",
    )


@app.get("/restaurant")
def restaurant():
    return success_response(
        {
            "name": RESTAURANT_NAME,
            "phone": RESTAURANT_PHONE,
            "email": RESTAURANT_EMAIL,
            "opening_hours": OPENING_HOURS,
            "generated_at": current_datetime(),
        }
    )


@app.get("/menu")
def get_menu():
    try:
        menu = search_engine.get_all_menu()
        return success_response(
            {
                "total_items": len(menu),
                "menu": menu,
            }
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/menu/search")
def search_menu(q: str):
    try:
        results = search_engine.search(q)
        return success_response(
            {
                "query": q,
                "count": len(results),
                "results": results,
            }
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return ChatResponse(
            answer=chatbot.chat(request.message)
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/order")
def place_order(order: OrderRequest):
    try:
        order_id = order_manager.place_order(
            customer_name=order.customer_name,
            phone=order.phone,
            email=order.email,
            address=order.address,
            payment_method=order.payment_method,
            items=[i.model_dump() for i in order.items],
        )

        return success_response(
            {
                "order_id": order_id,
                "status": "Preparing",
                "created_at": current_datetime(),
            }
        )

    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/orders")
def orders():
    return success_response(
        {
            "orders": order_manager.get_orders()
        }
    )


@app.get("/stats")
def stats():
    return success_response(
        {
            "chat_sessions": memory.total_sessions(),
            "messages": memory.total_messages(),
            "vector_documents": rag_engine.vector_store.size(),
            "orders": len(order_manager.get_orders()),
            "server_time": current_datetime(),
        }
    )


@app.get("/ping")
def ping():
    return {
        "message": "pong",
        "time": current_datetime(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
