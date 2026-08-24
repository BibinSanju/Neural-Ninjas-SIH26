import chromadb
from chromadb.utils import embedding_functions
import os

# Initialize ChromaDB client. We'll use a local persistent directory for the vector store.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "knowledge_base")
os.makedirs(DB_PATH, exist_ok=True)

# Note: BGE-Large is excellent for retrieval. Using the SentenceTransformer embedding function.
# The user's system will download the model weights on first run if not cached.
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")

client = chromadb.PersistentClient(path=DB_PATH)

try:
    collection = client.get_or_create_collection(name="internal_manuals", embedding_function=embedding_func)
except Exception as e:
    print(f"Warning: Could not initialize ChromaDB collection: {e}")
    collection = None

async def search_knowledge_base(query: str, n_results: int = 3) -> str:
    """
    Searches the local ChromaDB vector store for documents related to the query.
    Returns the most relevant chunks of text.
    """
    if not collection:
        return "Error: Knowledge base collection is not initialized."
        
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No relevant information found in the knowledge base."
            
        formatted_results = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
            
            # Extract rich metadata
            doc_name = metadata.get('document_name', 'Unknown')
            doc_type = metadata.get('type', 'Unknown')
            ingest_time = metadata.get('date_time_of_ingestion', 'Unknown')
            page_no = metadata.get('page_no', 'N/A')
            
            header = (
                f"--- Result {i+1} ---\n"
                f"Document: {doc_name} (Type: {doc_type})\n"
                f"Page: {page_no}\n"
                f"Ingested: {ingest_time}\n"
                f"Content:\n{doc}\n"
            )
            formatted_results.append(header)
            
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Search failed: {str(e)}"
