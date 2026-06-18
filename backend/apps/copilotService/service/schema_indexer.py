import os
# pyrefly: ignore [missing-import]
import chromadb
from sqlalchemy import create_engine, inspect
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma
# pyrefly: ignore [missing-import]
from langchain_huggingface import HuggingFaceEmbeddings

class SchemaIndexer:
    def __init__(self, db_url: str = None, chroma_url: str = "brain_chromadb", chroma_port: int = 8000):
        # Fallback to default if not set
        self.db_url = db_url or os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@db:5432/brain")
        self.engine = create_engine(self.db_url)
        
        # We use a lightweight local embedding model to avoid API rate limits for embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize ChromaDB client
        # For development, we connect to the Chroma docker container
        self.chroma_client = chromadb.HttpClient(host=chroma_url, port=chroma_port)
        
        # Create a collection for schemas
        self.collection_name = "db_schema"
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )

    def extract_schema(self):
        inspector = inspect(self.engine)
        schema_docs = []
        
        for table_name in inspector.get_table_names():
            # Skip some internal tables like alembic_version if they exist
            if table_name == "alembic_version":
                continue
                
            columns = inspector.get_columns(table_name)
            pk = inspector.get_pk_constraint(table_name)
            fks = inspector.get_foreign_keys(table_name)
            
            # Construct a clear description of the table
            desc_lines = [f"Table: {table_name}"]
            desc_lines.append("Columns:")
            for col in columns:
                col_name = col['name']
                col_type = str(col['type'])
                is_pk = " (PRIMARY KEY)" if pk and col_name in pk.get('constrained_columns', []) else ""
                # Find if it's a foreign key
                fk_str = ""
                for fk in fks:
                    if col_name in fk['constrained_columns']:
                        fk_str = f" (FOREIGN KEY to {fk['referred_table']}.{fk['referred_columns'][0]})"
                
                desc_lines.append(f"- {col_name}: {col_type}{is_pk}{fk_str}")
            
            table_text = "\n".join(desc_lines)
            schema_docs.append({
                "table": table_name,
                "text": table_text
            })
            
        return schema_docs

    def index_schema(self):
        print("Extracting schema from database...")
        docs = self.extract_schema()
        
        texts = [doc["text"] for doc in docs]
        metadatas = [{"table": doc["table"]} for doc in docs]
        
        print(f"Indexing {len(texts)} tables into ChromaDB...")
        
        # Clear existing collection if we want to re-index, or just add
        # The simplest way is to delete the collection and recreate
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
        except Exception:
            pass # Collection might not exist yet
            
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        print("Indexing complete.")
        
    def search_schema(self, query: str, k: int = 5):
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

if __name__ == "__main__":
    # If run directly, run the indexing
    chroma_host = os.getenv("CHROMA_HOST", "chromadb")
    indexer = SchemaIndexer(chroma_url=chroma_host, chroma_port=8000)
    indexer.index_schema()
