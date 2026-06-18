import pandas as pd

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st

api_key = st.secrets["OPENROUTER_API_KEY"]

def load_food_documents():
    docs = []

    for file_name in ["main_course.csv", "side_dish.csv"]:

        df = pd.read_csv(file_name)

        for _, row in df.iterrows():

            text = f"""
            Nama: {row.get('nama_asli', '')}
            Kalori: {row.get('kalori', '')}
            Protein: {row.get('protein', '')}
            Kategori: {row.get('kategori_asal', '')}
            Deskripsi: {row.get('saran_ai', '')}
            """

            docs.append(
                Document(page_content=text)
            )

    return docs

def build_food_vectorstore():

    docs = load_food_documents()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(
        docs,
        embeddings
    )

    return vectorstore

_vectorstore = None

def get_vectorstore():
    global _vectorstore

    if _vectorstore is None:
        _vectorstore = build_food_vectorstore()

    return _vectorstore


def search_food(query, k=5):

    vs = get_vectorstore()

    results = vs.similarity_search(
        query,
        k=k
    )

    return results

if __name__ == "__main__":

    vs = build_food_vectorstore()

    result = vs.similarity_search(
        "makanan tinggi protein untuk menaikkan berat badan",
        k=3
    )

    for r in result:
        print(r.page_content)