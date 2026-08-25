import sys
import os
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

# Ensure environment variables for Neo4j (Can be overridden via .env or system env)
os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI", "bolt://localhost:7687")
os.environ["NEO4J_USERNAME"] = os.getenv("NEO4J_USERNAME", "neo4j")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "industrial_password_2026")

# Lazy embeddings initialization to prevent server startup timeout during import
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    return _embeddings

async def search_knowledge_base(query: str, clearance_level: str) -> str:
    """
    Searches the GraphRAG Neo4j store for documents related to the query.
    Enforces Graph-Native RBAC based on clearance_level.
    """
    try:
        # We use a direct Cypher query for Hybrid Search + RBAC
        graph = Neo4jGraph(refresh_schema=False)
        graph.refresh_schema = lambda: None

        embeddings = get_embeddings()
        
        # We execute a vector search against the 'document_vector_index' 
        # But we filter nodes where node.clearance_level <= user_clearance
        # In Neo4j 5.x, db.index.vector.queryNodes is used.
        # However, to keep it simple, we can use the langchain Neo4jVector for similarity search, 
        # or we can write a raw Cypher query combining vector index and graph traversal.
        
        # Let's instantiate the Neo4jVector to get the underlying vector search
        vector_store = Neo4jVector.from_existing_index(
            embedding=embeddings,
            index_name="document_vector_index",
            keyword_index_name="document_keyword_index",

            search_type="vector"
        )
        
        # We can use similarity_search with a metadata filter!
        # This will filter at the DB level, enforcing RBAC natively.
        results = vector_store.similarity_search(
            query=query, 
            k=3,
            filter={"clearance_level": {"$lte": int(clearance_level)}}
        )
        
        if not results:
            return "No relevant information found in the knowledge base within your clearance level."
            
        formatted_results = []
        for i, doc in enumerate(results):
            metadata = doc.metadata
            doc_name = metadata.get('document_name', 'Unknown')
            doc_type = metadata.get('type', 'Unknown')
            ingest_time = metadata.get('date_time_of_ingestion', 'Unknown')
            page_no = metadata.get('page_no', 'N/A')
            doc_clearance = metadata.get('clearance_level', 'N/A')
            
            # Additional Graph Traversal Context
            # For a true GraphRAG, we also fetch connected graph nodes (Concepts/Components)
            # extracted by the LLMGraphTransformer.
            doc_id = metadata.get('doc_id')
            graph_context = ""
            if doc_id:
                # Find connected nodes with clearance verification
                user_clearance_int = int(clearance_level) if clearance_level and clearance_level.isdigit() else 1
                traversal_query = '''
                MATCH (d:Document {doc_id: $doc_id})-[r]-(connected)
                WHERE connected.clearance_level IS NULL OR connected.clearance_level <= $user_clearance
                RETURN type(r) as rel, labels(connected) as labels, connected.id as name
                LIMIT 5
                '''
                connected_nodes = graph.query(traversal_query, params={"doc_id": doc_id, "user_clearance": user_clearance_int})
                if connected_nodes:
                    graph_context = "\nLinked Graph Entities:\n"
                    for rel in connected_nodes:
                        graph_context += f" - [{rel['rel']}] -> {rel['labels'][0]}: {rel['name']}\n"
            
            header = (
                f"--- Result {i+1} ---\n"
                f"Document: {doc_name} (Type: {doc_type})\n"
                f"Page: {page_no}\n"
                f"Ingested: {ingest_time}\n"
                f"Clearance Level: {doc_clearance}\n"
                f"Content:\n{doc.page_content}\n"
                f"{graph_context}"
            )
            formatted_results.append(header)
            
        return "\n".join(formatted_results)
    except Exception as e:
        return f"GraphRAG Search failed: {str(e)}"
