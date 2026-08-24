import os
import argparse
import datetime
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

# Define the absolute path to our ChromaDB store so the scripts and the mcp_server share the same DB
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mcp_server", "knowledge_base")

def get_chroma_collection():
    os.makedirs(DB_PATH, exist_ok=True)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(
        name="internal_manuals", 
        embedding_function=embedding_func
    )

def ingest_file(filepath: str, doc_id: str, original_filename: str):
    print(f"Starting ingestion for: {original_filename} (ID: {doc_id}) from path: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return

    # Use original filename for the extension to know how to parse it
    file_extension = os.path.splitext(original_filename)[1].lower()
    doc_type = file_extension.lstrip('.')
    ingestion_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Load Document
    print(f"Loading document...")
    if file_extension == '.pdf':
        loader = PyPDFLoader(filepath)
        docs = loader.load()
    elif file_extension in ['.txt', '.md', '.csv']:
        loader = TextLoader(filepath, encoding='utf-8')
        docs = loader.load()
    else:
        print(f"Unsupported file type: {file_extension}. Supported types: pdf, txt, md, csv")
        return

    # 2. Advanced Chunking
    print(f"Splitting document into optimal chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    
    # 3. Enrich Metadata
    print(f"Enriching metadata for {len(chunks)} chunks...")
    texts = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        page_no = chunk.metadata.get('page', 'N/A')
        if page_no != 'N/A':
            page_no = str(page_no + 1)
            
        enriched_metadata = {
            "doc_id": doc_id,
            "document_name": original_filename,
            "type": doc_type,
            "date_time_of_ingestion": ingestion_time,
            "page_no": page_no,
            "source": filepath
        }
        
        texts.append(chunk.page_content)
        metadatas.append(enriched_metadata)
        # Use doc_id as the prefix so they are globally unique for this document
        ids.append(f"{doc_id}_chunk_{i}")

    # 4. Load into ChromaDB
    print(f"Initializing Vector Store at {DB_PATH}")
    collection = get_chroma_collection()
    
    print("Saving chunks to ChromaDB...")
    collection.upsert(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    print("Ingestion complete!")

def delete_document(doc_id: str):
    """Deletes all chunks associated with a specific doc_id from ChromaDB."""
    print(f"Attempting to delete document with ID: {doc_id}")
    try:
        collection = get_chroma_collection()
        collection.delete(where={"doc_id": doc_id})
        print(f"Successfully deleted document chunks for ID: {doc_id}")
    except Exception as e:
        print(f"Failed to delete document {doc_id}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage documents in the local RAG knowledge base.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a document into the knowledge base")
    ingest_parser.add_argument("filepath", type=str, help="Physical path to the file on disk")
    ingest_parser.add_argument("doc_id", type=str, help="UUID or unique identifier for the document")
    ingest_parser.add_argument("original_filename", type=str, help="Original name of the file (e.g. manual.pdf)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a document from the knowledge base")
    delete_parser.add_argument("doc_id", type=str, help="UUID or unique identifier of the document to delete")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest_file(args.filepath, args.doc_id, args.original_filename)
    elif args.command == "delete":
        delete_document(args.doc_id)
    else:
        parser.print_help()
