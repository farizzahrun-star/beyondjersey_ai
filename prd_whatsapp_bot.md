# PRD: WhatsApp AI Chatbot - Beyond Jersey

## 1. Overview

**Product Name:** Beyond Jersey AI Assistant
**Platform:** WhatsApp Business API
**Tujuan:** Otomasi respons pertanyaan repetitif (harga, pembayaran, dll.) dan eskalasi ke live agent ketika diperlukan.

---

## 2. Problem Statement

Tim CS Beyond Jersey saat ini menangani banyak pesan WhatsApp berulang seperti:
- "Berapa harga jersey X?"
- "Bisa COD nggak?"
- "Cara ordernya gimana?"

Ini memakan waktu CS dan memperlambat respons ke pelanggan yang membutuhkan bantuan lebih kompleks.

---

## 3. Goals & Success Metrics

| Goal | Metric |
|------|--------|
| Kurangi beban CS untuk pertanyaan repetitif | ≥ 70% chat tertangani bot tanpa eskalasi |
| Respons lebih cepat | Waktu respons < 5 detik (24/7) |
| Kepuasan pelanggan terjaga | Rating kepuasan ≥ 4/5 |
| Eskalasi tepat sasaran | ≤ 30% chat dieskalasi ke live agent |

---

## 4. Scope

### ✅ In Scope
- Balas pertanyaan soal **harga produk**
- Balas pertanyaan soal **sistem pembayaran** (transfer, QRIS, COD, dll.)
- Balas pertanyaan soal **cara order**
- Balas pertanyaan soal **status order** (jika terintegrasi DB)
- Balas pertanyaan soal **varian & ketersediaan stok**
- **Eskalasi ke live agent** untuk:
  - Komplain & retur
  - Pertanyaan di luar database
  - Permintaan negosiasi harga
  - Konfirmasi pembayaran manual

### ❌ Out of Scope (V1)
- Integrasi payment gateway otomatis
- Pemrosesan order otomatis
- Notifikasi pengiriman real-time

---

## 5. User Journey

```
Pelanggan kirim pesan
        │
        ▼
  Bot menyapa & tanya kebutuhan
        │
        ├──► Pertanyaan harga / produk
        │         └──► Bot jawab dari database produk
        │
        ├──► Pertanyaan pembayaran
        │         └──► Bot jelaskan metode & rekening
        │
        ├──► Ingin order / bayar
        │         └──► Bot kirim panduan + eskalasi ke CS
        │
        └──► Di luar kemampuan bot
                  └──► "Menghubungkan ke tim kami..."
                            └──► Live Agent ambil alih
```

---

## 6. Fitur Detail

### 6.1 Greeting & Main Menu
- Bot auto-reply saat pesan masuk pertama
- Tampilkan menu pilihan (harga, cara order, pembayaran, lainnya)
- Deteksi keyword untuk skip menu langsung ke jawaban

### 6.2 Katalog Harga
- Bot bisa jawab pertanyaan harga berdasarkan:
  - Nama produk / tim / liga
  - Grade jersey (Grade Ori, AAA, Player Issue)
  - Varian (home/away/third, ukuran)
- Jawaban berformat rapi dengan info lengkap

### 6.3 Informasi Pembayaran
- Daftar metode pembayaran yang tersedia
- Nomor rekening / QRIS
- Ketentuan DP & pelunasan
- Estimasi waktu konfirmasi pembayaran

### 6.4 Cara Order
- Step-by-step panduan order
- Informasi custom name & number
- Estimasi produksi & pengiriman

### 6.5 Handover ke Live Agent
**Trigger eskalasi:**
- Pelanggan ketik "hubungi CS", "mau bayar", "komplain", dll.
- Bot tidak menemukan jawaban di database
- Pelanggan sudah 2x bertanya hal yang sama tanpa jawaban memuaskan
- Permintaan negosiasi

**Mekanisme:**
- Bot kirim pesan: *"Oke, menghubungkan kamu ke tim kami sekarang ya! Mohon tunggu sebentar 🙏"*
- Notifikasi ke CS bahwa ada chat masuk
- CS ambil alih percakapan

---

## 7. Tech Stack (Rekomendasi)

| Komponen | Pilihan |
|----------|---------|
| WhatsApp API | WhatsApp Business API (via Twilio / WABA langsung) |
| AI/NLP | OpenAI GPT-4o (dengan function calling) |
| Backend | Node.js / Python FastAPI |
| Database Produk | Supabase / Google Sheets (tahap awal) |
| Live Chat Platform | Respond.io / Wati.io / Qiscus |
| Hosting | Railway / Vercel / VPS |

---

## 8. Database Struktur (Minimal)

```
products
├── id
├── name (nama produk/klub)
├── grade
├── price
├── variants (ukuran, home/away)
└── stock_status

payment_methods
├── method_name
├── account_number
├── account_name
└── notes

faqs
├── question_keyword
└── answer_text
```

---

## 9. Bot Persona

- **Nama:** Jersy (mascot Beyond Jersey)
- **Tone:** Friendly, helpful, casual tapi profesional
- **Bahasa:** Indonesia (bisa switch ke English jika pelanggan pakai English)
- **Emoji:** Digunakan secukupnya untuk kesan ramah ✅

---

## 10. Alur Eskalasi & SLA

| Kondisi | Tindakan Bot | Target Respons CS |
|---------|-------------|-------------------|
| Ingin bayar/order | Eskalasi + notif CS | ≤ 5 menit |
| Komplain | Eskalasi prioritas + notif CS | ≤ 2 menit |
| Di luar database | Eskalasi + log pertanyaan | ≤ 10 menit |
| CS tidak tersedia (offline) | Bot kirim pesan "CS kami sedang offline, akan balas segera" | - |

---

## 11. Phases / Roadmap

| Phase | Scope | Timeline |
|-------|-------|----------|
| **V1 - MVP** | Greeting, FAQ harga & pembayaran, eskalasi manual | 3-4 minggu |
| **V2** | Integrasi database produk real-time, deteksi intent lebih akurat | +4 minggu |
| **V3** | Order tracking, notifikasi otomatis, analitik dashboard | +6 minggu |

---

## 12. Risiko & Mitigasi

| Risiko | Mitigasi |
|--------|----------|
| Bot salah jawab harga | Tambahkan disclaimer "harga bisa berubah, konfirmasi ke CS" |
| Pelanggan frustasi dengan bot | Sediakan opsi "Bicara ke CS" di setiap langkah |
| Data produk tidak up-to-date | Buat sistem update database yang mudah (Google Sheets) |
| WhatsApp API rate limit | Implementasi queue system |