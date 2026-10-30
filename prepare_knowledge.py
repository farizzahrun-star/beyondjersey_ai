
from pathlib import Path

DATABASE_DIR = Path("app/database")

FILES = [
    DATABASE_DIR / "faq_beyond_jersey.md",
    DATABASE_DIR / "katalog_produk_beyond_jersey.md",
]

documents = []

for file_path in FILES:
    if not file_path.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {file_path}"
        )

    text = file_path.read_text(encoding="utf-8").strip()

    documents.append({
        "source": file_path.name,
        "text": text,
    })

    print(f"File: {file_path.name}")
    print(f"Jumlah karakter: {len(text):,}")
    print("-" * 40)

print(f"Total dokumen berhasil dibaca: {len(documents)}")
