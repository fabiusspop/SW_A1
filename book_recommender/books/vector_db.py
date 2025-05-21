import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from .xml_utils import get_books_from_xml

chroma_client = chromadb.Client()
collection = chroma_client.create_collection("books")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def build_vector_db():
    books, _ = get_books_from_xml()
    for idx, book in enumerate(books):
        # Convert lists to comma-separated strings for metadata
        meta = {
            'title': book.get('title', ''),
            'themes': ', '.join(book.get('themes', [])),
            'reading_levels': ', '.join(book.get('reading_levels', [])),
            'author': book.get('author', '')
        }
        text = f"{meta['title']} {meta['themes']} {meta['reading_levels']} {meta['author']}"
        embedding = embedder.encode(text).tolist()
        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[str(idx)],
            metadatas=[meta]
        )

def query_vector_db(query, top_k=3):
    embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    # results['metadatas'] will be a list containing one list of metadata dictionaries if successful
    # We want the inner list of metadata dictionaries. Handle cases where metadatas or the inner list might be empty.
    return results.get('metadatas', [[]])[0] if results.get('metadatas') and results.get('metadatas')[0] else []

def search_by_theme_and_author(theme, author):
    books, _ = get_books_from_xml()
    results = []
    for book in books:
        if theme.lower() in [t.lower() for t in book.get('themes', [])] and author.lower() in book.get('author', '').lower():
            results.append(book)
    return results 