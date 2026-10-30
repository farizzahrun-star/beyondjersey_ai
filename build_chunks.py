
from pathlib import Path
import re

DATABASE_DIR = Path("app/database")

FILES = [
    DATABASE_DIR / "faq_beyond_jersey.md",
    DATABASE_DIR / "katalog_produk_beyond_jersey.md",
]


def split_markdown(text):
    sections = re.split(r"(?m)(?=^##\s+)", text.strip())
    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        if section.startswith("# ") and not re.search(
            r"(?m)^##\s+", section
        ):
            continue

        chunks.append(section)

    return chunks


all_chunks = []

for file_path in FILES:
    if not file_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    sections = split_markdown(text)

    for section in sections:
        heading = re.match(r"^##\s+(.+)", section)

        all_chunks.append({
            "text": section,
            "source": file_path.name,
            "section": heading.group(1) if heading else "Tanpa judul",
        })

print(f"Total chunks: {len(all_chunks)}")

for i, chunk in enumerate(all_chunks, start=1):
    print(f"\nChunk {i}")
    print(f"Source: {chunk['source']}")
    print(f"Section: {chunk['section']}")
    print(f"Karakter: {len(chunk['text'])}")

print("\n=== CONTOH ISI CHUNK ===")

for i, chunk in enumerate(all_chunks, start=1):
    if chunk["section"] == "2. COMO 26/27":
        print(f"\nSumber: {chunk['source']}")
        print(f"Bagian: {chunk['section']}")
        print(chunk["text"])
