"""
=========================================================
Meeple Cafe AI Ordering Chatbot
Build FAISS Vector Database
Version : 4.0.0
Author  : Sugumar R
=========================================================
"""

import pickle
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from google import genai

from backend.config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
    MENU_FILE,
    VECTOR_DB_DIR,
    FAISS_INDEX,
    METADATA_FILE,
)

# ==========================================================
# Gemini Client
# ==========================================================

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================================
# Vector Builder
# ==========================================================


class VectorDatabaseBuilder:

    def __init__(self):

        self.menu = pd.read_csv(MENU_FILE)

        self.menu.fillna("", inplace=True)

        VECTOR_DB_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ======================================================
    # Convert Row → Search Text
    # ======================================================

    def row_to_text(self, row):

        parts = []

        for value in row.values:
            if str(value).strip():
                parts.append(str(value))

        return " | ".join(parts)

    # ======================================================
    # Gemini Embedding
    # ======================================================

    def embedding(self, text):

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )

        return np.array(
            response.embeddings[0].values,
            dtype=np.float32,
        )

    # ======================================================
    # Build Index
    # ======================================================

    def build(self):

        embeddings = []

        metadata = []

        print("=" * 60)
        print("Building Gemini Vector Database")
        print("=" * 60)

        total = len(self.menu)

        for index, row in self.menu.iterrows():

            text = self.row_to_text(row)

            vector = self.embedding(text)

            embeddings.append(vector)

            metadata.append(
                {
                    "id": index,
                    "text": text,
                    "record": row.to_dict(),
                }
            )

            print(f"[{index + 1}/{total}] Embedded")

        vectors = np.vstack(embeddings)

        dimension = vectors.shape[1]

        index = faiss.IndexFlatL2(dimension)

        index.add(vectors)

        faiss.write_index(index, str(FAISS_INDEX))

        with open(METADATA_FILE, "wb") as file:
            pickle.dump(metadata, file)

        print()
        print("=" * 60)
        print("Vector Database Created Successfully")
        print("=" * 60)
        print(f"Documents : {len(metadata)}")
        print(f"Dimension : {dimension}")
        print(f"Index File : {FAISS_INDEX}")
        print(f"Metadata   : {METADATA_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    builder = VectorDatabaseBuilder()

    builder.build()
