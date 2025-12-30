import chromadb
from chromadb.config import Settings
from langchain.embeddings import init_embeddings

client = chromadb.Client(
    Settings(persist_directory="vectorstore")
)

collection = client.get_or_create_collection("sunbeam")

embedding_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

def store_chunks(chunks, metadata):
    vectors = embedding_model.embed_documents(chunks)
    for i, vec in enumerate(vectors):
        collection.add(
            documents=[chunks[i]],
            embeddings=[vec],
            metadatas=[metadata],
            ids=[f"{metadata['source']}_{i}"]
        )

def search_db(query):
    qvec = embedding_model.embed_query(query)
    results = collection.query(query_embeddings=[qvec], n_results=5)
    return results["documents"][0]
