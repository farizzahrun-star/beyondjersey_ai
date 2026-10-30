
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

COLLECTION_NAME = "beyond_jersey_embedding_test"
VECTOR_NAME = "all-minilm-l6-v2"
MODEL_NAME = "sentence-transformers/all-minilm-l6-v2"

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
    cloud_inference=True,
)

try:
    # Buat collection sementara yang terisolasi dari collection utama
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            VECTOR_NAME: models.VectorParams(
                size=384,
                distance=models.Distance.COSINE,
            )
        },
    )

    print("Collection pengujian berhasil dibuat.")

    # Kirim dokumen dengan nama named vector yang sesuai
    point = models.PointStruct(
        id=1,
        vector={
            VECTOR_NAME: models.Document(
                text="Harga jersey Como Home 26/27 adalah Rp3.600.000 tanpa nameset.",
                model=MODEL_NAME,
            )
        },
        payload={
            "source": "test_embedding.py",
            "text": "Harga jersey Como Home 26/27 adalah Rp3.600.000 tanpa nameset.",
        },
    )

    response = client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
        wait=True,
    )

    print("Status upload:", response.status)

    # Verifikasi penyimpanan
    count = client.count(
        collection_name=COLLECTION_NAME,
        exact=True,
    ).count

    result = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[1],
        with_payload=True,
        with_vectors=False,
    )

    print("Jumlah points:", count)
    print("Point ditemukan:", len(result))

    if count == 1 and len(result) == 1:
        print("BERHASIL: Point tersimpan dan dapat dibaca.")
        print("Payload:", result[0].payload)
    else:
        print("BELUM BERHASIL: Point belum tersimpan sesuai harapan.")

except Exception as e:
    print("TES GAGAL")
    print("Jenis error:", type(e).__name__)
    print("Detail:", e)

finally:
    try:
        if client.collection_exists(COLLECTION_NAME):
            client.delete_collection(COLLECTION_NAME)
            print("Collection pengujian sudah dihapus.")
    except Exception as cleanup_error:
        print("Gagal membersihkan collection:", cleanup_error)
