
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)

info = client.get_collection("beyond_jersey_faq")

print("Collection berhasil diakses.")
print("Status:", info.status)
print("Jumlah points:", info.points_count)
print("Konfigurasi vector:")
print(info.config.params.vectors)
print("Konfigurasi sparse vector:")
print(info.config.params.sparse_vectors)
