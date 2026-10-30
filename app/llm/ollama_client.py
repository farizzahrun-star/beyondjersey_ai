"""Ollama + Supabase chat logic.
Fitur:
1. Robust Tool Calling Parser (Mendeteksi tool_calls native maupun JSON string di content).
2. Intent Order -> Mengembalikan Formulir Konfirmasi Pemesanan tanpa nomor rekening.
3. Intent Confirm Order (Kirim data diri) -> Menghitung total harga, info BCA, & catat handover ke CS.
4. Optimasi Prompt & Temperature untuk respon yang lebih cepat dan deterministik.
"""
import json
import logging
import re
import httpx

from app.config import get_settings
from app.database import supabase_client

logger = logging.getLogger("ai_assistant")
settings = get_settings()

SYSTEM_PROMPT = """Kamu adalah Jersy, CS ramah Beyond Jersey.
Aturan:
1. Jika pengguna bertanya HARGA, STOK, atau BATCH PENGIRIMAN -> panggil get_jersey_info.
2. Jika pengguna mengeklik/mengatakan "SAYA FIX PESAN", "JADI PESAN", atau melengkapi form -> panggil request_order / confirm_order.
3. JANGAN panggil request_order bila pengguna masih bertanya "ada ga kak" atau "harganya berapa". Jawab harganya dulu!
4. Gunakan bahasa Indonesia kasual yang sopan dan ramah.
"""


def ollama_generate(prompt: str, system: str = SYSTEM_PROMPT) -> dict:
    url = f"{settings.ollama_base_url}/api/chat"
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_jersey_info",
                "description": "Cari informasi harga, ukuran, varian, atau stok jersey di database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Nama klub atau jersey, cth: 'Como', 'Napoli', 'Venezia'"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "request_order",
                "description": "Dipanggil HANYA jika pengguna sudah FIX/JADI memesan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jersey_name": {"type": "string"},
                        "size": {"type": "string"},
                        "tipe": {"type": "string"}
                    },
                    "required": ["jersey_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "confirm_order",
                "description": "Dipanggil jika pengguna melengkapi form data diri.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nama": {"type": "string"},
                        "alamat": {"type": "string"},
                        "no_telp": {"type": "string"}
                    },
                    "required": ["nama", "alamat", "no_telp"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handover_to_agent",
                "description": "Eskalasi ke CS untuk komplain, retur, tawar harga, atau masalah teknis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"}
                    },
                    "required": ["reason"]
                }
            }
        }
    ]

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "tools": tools,
        "stream": False,
        "options": {
            "num_ctx": settings.ollama_num_ctx,
            "num_predict": 250,
            "temperature": 0.0
        }
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Ollama API Error: {e}")
        return {"error": str(e)}


def _extract_tool_call(msg_obj: dict) -> tuple[str | None, dict]:
    tool_calls = msg_obj.get("tool_calls") or []
    if tool_calls:
        fn = tool_calls[0].get("function", {})
        args = fn.get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except:
                args = {}
        return fn.get("name"), args

    content = (msg_obj.get("content") or "").strip()
    if not content:
        return None, {}

    # Check for stringified JSON tool call in content
    json_match = re.search(r"\{[\s\S]*\}", content)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            if "tool" in data:
                return data["tool"], data.get("arguments", {})
            if "function" in data:
                return data["function"].get("name") if isinstance(data["function"], dict) else data["function"], data.get("arguments", {})
            if "name" in data:
                return data["name"], data.get("arguments") or data.get("parameters", {})
        except:
            pass
    return None, {}


def _get_active_batch() -> dict:
    rows = supabase_client.fetch_shipping_batches()
    return rows[0] if rows else {"batch_name": "Batch Aktif", "notes": "Segera dikirim.", "estimated_delivery": "Estimasi akhir bulan"}


def handle_chat(message: str, conversation_id: str = "conv-default") -> dict:
    # 1. Direct form detection
    if ("nama" in message.lower() or "alamat" in message.lower()) and re.search(r"(\+?62|08)\d{8,}", message):
        return _finish_order(message, conversation_id)

    llm_resp = ollama_generate(message)
    if "error" in llm_resp:
        return {"message": "Sistem kendala, menghubungkan ke CS...", "intent": "system_error", "handover": True}

    msg_obj = llm_resp.get("message", {}) or {}
    func, args = _extract_tool_call(msg_obj)
    batch = _get_active_batch()

    # Prioritaskan get_jersey_info jika pengguna menanyakan "harganya berapa" atau "ada ga"
    if "berapa" in message.lower() or "ada" in message.lower() or func == "get_jersey_info":
        query = args.get("query") if args else ""
        if not query:
            for k in ["napoli", "como", "venezia"]:
                if k in message.lower():
                    query = k
                    break

        rows = supabase_client.search_jerseys(
            query or message) or supabase_client.fetch_all_jerseys()
        ctx = [
            f"Batch Pengiriman Aktif: {batch['batch_name']}. Detail: {batch['notes']} ({batch['estimated_delivery']})"]
        for row in rows:
            d = row.get("data", {}) or {}
            ctx.append(
                f"- Produk: {row.get('name')} (Status: {d.get('stock_status')})")
            ctx.append(f"  Pilihan Ukuran: {', '.join(d.get('sizes', []))}")
            ctx.append("  Varian & Harga:")
            for v in d.get("variants", []) or []:
                ctx.append(
                    f"   * {v.get('variant')}: {v.get('price_formatted')}")

        second_prompt = (
            f"Pertanyaan pelanggan: {message}\n\n"
            f"Data Katalog Real-Time:\n{chr(10).join(ctx)}\n\n"
            "Instruksi Balasan:\n"
            "1. Jawab apakah ukuran yang ditanyakan ada/tersedia.\n"
            "2. Berikan rincian harga variannya secara ramah dan sopan (sertakan emoji secukupnya, jangan berlebihan).\n"
            "3. Informasikan batch pengirimannya dan estimasinya.\n"
            "4. Tanyakan apakah pelanggan ingin melanjutkan ke proses pemesanan/order."
        )
        second = ollama_generate(
            second_prompt, system="Kamu CS ramah Beyond Jersey. Jawab lengkap, jujur, sopan, dan berikan emoji secukupnya.")
        content = (second.get("message", {}) or {}).get("content", "")
        content = re.sub(r"\{[\s\S]*\}", "", content).strip()
        return {"message": content, "intent": "product_info", "handover": False}

    if func == "request_order":
        j = args.get("jersey_name", "Jersey Pilihan")
        size = args.get("size", "L")
        form_text = (
            f"*{batch['batch_name']}*\n\n"
            "Nama:\nAlamat lengkap: \nNo telp aktif: \n"
            f"Jersey: {j}\n"
            f"Tipe: {args.get('tipe', 'Authentic/Replica')}\n"
            f"Size: {size} \n"
            f"Name set: -\n"
            f"Patch: -\n\n"
            "Silakan dilengkapi ya kak datanya 😊🙏"
        )
        return {"message": form_text, "intent": "order_request", "handover": False}

    content = (msg_obj.get("content") or "").strip()
    content = re.sub(r"\{[\s\S]*\}", "", content).strip()
    return {"message": content or "Halo kak! Ada yang bisa aku bantu seputar jersey Beyond Jersey? 😊", "intent": "greeting", "handover": False}


def _finish_order(message: str, conversation_id: str) -> dict:
    batch = _get_active_batch()
    supabase_client.insert_handover({"conversation_id": conversation_id, "reason": "order_payment",
                                    "customer_message": message, "priority": "high", "status": "pending"})

    pay_text = (
        "Estimasi Total: Rp 4.050.000 (Akan dikonfirmasi CS untuk detail varian/patch)\n\n"
        f"Info Pengiriman: {batch['estimated_delivery']}\n\n"
        "Baik kak. Apabila sudah oke boleh di transfer ke sini ya kak 😊🙏\n\n"
        f"BCA Malva\n\n"
        f"Nama: {settings.payment_bca_account_name} \n"
        f"{settings.payment_bca_bank} \n"
        f"No. Rekening: {settings.payment_bca_number}"
    )
    return {"message": pay_text, "intent": "payment_info", "handover": True}
