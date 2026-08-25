import os
import argparse
import datetime
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_ollama import ChatOllama

# Ensure environment variables for Neo4j (used automatically by Neo4jGraph)
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "industrial_password_2026"

def ingest_file(filepath: str, doc_id: str, original_filename: str, clearance_level: str):
    print(f"Starting GraphRAG ingestion for: {original_filename} (ID: {doc_id}) with Clearance: {clearance_level}")
    
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
    
    # Enrich metadata for the base chunks before graph extraction
    for i, chunk in enumerate(chunks):
        page_no = chunk.metadata.get('page', 'N/A')
        if page_no != 'N/A':
            page_no = str(page_no + 1)
            
        chunk.metadata.update({
            "doc_id": doc_id,
            "document_name": original_filename,
            "type": doc_type,
            "date_time_of_ingestion": ingestion_time,
            "page_no": page_no,
            "source": filepath,
            "clearance_level": int(clearance_level)  # Store as integer for numerical comparison
        })

    # 3. Extract Graph Nodes & Relationships using LLM
    print(f"Extracting graph entities and relationships using Llama3.1...")
    # NOTE: Using llama3.1
    llm = ChatOllama(model="llama3.1", temperature=0)
    llm_transformer = LLMGraphTransformer(llm=llm)
    
    # Process graph extraction
    graph_documents = llm_transformer.convert_to_graph_documents(chunks)
    
    # Enrich the extracted Graph Nodes with the RBAC clearance level
    for graph_doc in graph_documents:
        # Also copy standard metadata to graph source document
        graph_doc.source.metadata.update({
            "doc_id": doc_id,
            "clearance_level": int(clearance_level)
        })
        for node in graph_doc.nodes:
            # We must assign the clearance_level to the node itself so Cypher queries can filter by it
            node.properties = node.properties or {}
            node.properties["clearance_level"] = int(clearance_level)
            node.properties["doc_id"] = doc_id

    # 4. Save to Neo4j
    print(f"Connecting to Neo4j...")
    try:
        graph = Neo4jGraph(refresh_schema=False)
        graph.refresh_schema = lambda: None
        
        print(f"Saving graph documents to Neo4j using custom Cypher...")
        for graph_doc in graph_documents:
            # Insert source document
            doc_id = graph_doc.source.metadata["doc_id"]
            # Convert text to string if it isn't, and ensure properties are dict
            props = graph_doc.source.metadata
            props["text"] = graph_doc.source.page_content
            
            query_doc = "MERGE (d:Document {doc_id: $doc_id}) SET d += $properties"
            graph.query(query_doc, params={"doc_id": doc_id, "properties": props})
            
            # Insert nodes
            for node in graph_doc.nodes:
                # Create entity node with base label __Entity__ and specific label
                query_node = f"MERGE (n:`__Entity__` {{id: $id}}) SET n:`{node.type}` SET n += $properties MERGE (d:Document {{doc_id: $doc_id}})-[:MENTIONS]->(n)"
                graph.query(query_node, params={"id": node.id, "properties": node.properties, "doc_id": doc_id})
                
            # Insert relationships
            for rel in graph_doc.relationships:
                query_rel = f"MATCH (source:`{rel.source.type}` {{id: $source_id}}), (target:`{rel.target.type}` {{id: $target_id}}) MERGE (source)-[r:`{rel.type}`]->(target) SET r += $properties"
                graph.query(query_rel, params={"source_id": rel.source.id, "target_id": rel.target.id, "properties": rel.properties or {}})
        
        # 5. Create Vector Index on Document Chunks
        # This allows us to use Neo4jVector for the hybrid search later
        print(f"Creating/Updating Vector Index on Neo4j for semantic search...")
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
        
        # The Document nodes were created by include_source=True. We want to index their text property.
        Neo4jVector.from_existing_graph(
            embedding=embeddings,
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["text"],
            embedding_node_property="embedding",
            index_name="document_vector_index",
            keyword_index_name="document_keyword_index"
        )
    except Exception as e:
        print(f"Warning: Could not connect to Neo4j or save graph data. Skipping Neo4j ingestion. Error: {e}")
    
    print("GraphRAG Ingestion complete!")

def delete_document(doc_id: str):
    """Deletes all nodes and relationships associated with a specific doc_id from Neo4j."""
    print(f"Attempting to delete document with ID: {doc_id} from Neo4j")
    try:
        graph = Neo4jGraph(refresh_schema=False)
        graph.refresh_schema = lambda: None
        # Delete nodes that have the doc_id property
        # Use APOC or basic Cypher
        query = '''
        MATCH (n)
        WHERE n.doc_id = $doc_id
        DETACH DELETE n
        '''
        graph.query(query, params={"doc_id": doc_id})
        print(f"Successfully deleted document graph nodes for ID: {doc_id}")
    except Exception as e:
        print(f"Failed to delete document {doc_id}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage documents in the Neo4j GraphRAG knowledge base.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a document into the graph knowledge base")
    ingest_parser.add_argument("filepath", type=str, help="Physical path to the file on disk")
    ingest_parser.add_argument("doc_id", type=str, help="UUID or unique identifier for the document")
    ingest_parser.add_argument("original_filename", type=str, help="Original name of the file (e.g. manual.pdf)")
    ingest_parser.add_argument("clearance_level", type=str, help="RBAC Clearance level for the document")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a document from the graph knowledge base")
    delete_parser.add_argument("doc_id", type=str, help="UUID or unique identifier of the document to delete")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest_file(args.filepath, args.doc_id, args.original_filename, args.clearance_level)
    elif args.command == "delete":
        delete_document(args.doc_id)
    else:
        parser.print_help()
