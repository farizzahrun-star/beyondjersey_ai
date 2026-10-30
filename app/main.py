import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.database import supabase_client
from app.llm.ollama_client import handle_chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("beyond_jersey")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="WhatsApp AI Chatbot MVP — Beyond Jersey (Qwen3 via Ollama + Supabase)",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    conversation_id: str = Field(default="demo-001")
    customer_id: str = Field(default="customer-001")
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    intent: str
    handover: bool
    response_time_seconds: float | None = None


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "app_name": settings.app_name,
        "ollama_model": settings.ollama_model,
        "ollama_base_url": settings.ollama_base_url,
        "supabase_connected": bool(settings.supabase_url and settings.supabase_anon_key),
        "current_po_batch": settings.current_po_batch,
    }


@app.get("/jerseys")
@app.get("/products")
def get_jerseys():
    try:
        return supabase_client.fetch_all_jerseys()
    except Exception as e:
        logger.error(f"Failed to fetch jerseys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payment-methods")
def get_payment_methods():
    return {
        "bank": settings.payment_bca_bank,
        "account_name": settings.payment_bca_account_name,
        "account_number": settings.payment_bca_number,
        "note": "Transfer konfirmasi ke CS setelah mengisi form pesanan.",
    }


@app.get("/faqs")
def get_faqs():
    return [
        {
            "question": "Cara order",
            "answer": "Sebutkan jersey, ukuran, tipe, nameset/patch yang diinginkan. Bot akan kirim form konfirmasi.",
        },
        {
            "question": "Pengiriman",
            "answer": f"{settings.current_po_batch}. Estimasi PO per batch bulanan.",
        },
    ]


@app.post("/handover")
def create_handover(payload: dict):
    try:
        return supabase_client.insert_handover(payload)
    except Exception as e:
        logger.error(f"Handover insert failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    start = time.time()
    logger.info(
        f"[{req.conversation_id}] IN  customer={req.customer_id} msg={req.message!r}")
    try:
        result = handle_chat(req.message, conversation_id=req.conversation_id)
        elapsed = round(time.time() - start, 2)
        logger.info(
            f"[{req.conversation_id}] OUT intent={result.get('intent')} "
            f"handover={result.get('handover')} time={elapsed}s"
        )
        return ChatResponse(
            conversation_id=req.conversation_id,
            message=result.get("message", ""),
            intent=result.get("intent", "unknown"),
            handover=bool(result.get("handover", False)),
            response_time_seconds=elapsed,
        )
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.exception(
            f"[{req.conversation_id}] ERROR after {elapsed}s: {e}")
        return ChatResponse(
            conversation_id=req.conversation_id,
            message="Maaf kak, sistem kami sedang mengalami kendala. Sebentar ya, aku bantu hubungkan ke tim CS kami 🙏",
            intent="system_error",
            handover=True,
            response_time_seconds=elapsed,
        )
