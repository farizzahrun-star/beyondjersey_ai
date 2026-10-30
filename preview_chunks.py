
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

        # Abaikan judul dokumen yang tidak memiliki isi.
        if section.startswith("# ") and not re.search(
            r"(?m)^##\s+", section
        ):
            continue

        chunks.append(section)

    return chunks


for file_path in FILES:
    text = file_path.read_text(encoding="utf-8")
    chunks = split_markdown(text)

    print(f"\n{'=' * 60}")
    print(f"FILE: {file_path.name}")
    print(f"JUMLAH CHUNKS: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n--- CHUNK {i} | {len(chunk)} karakter ---")
        print(chunk[:300])
        if len(chunk) > 300:
            print("...")
