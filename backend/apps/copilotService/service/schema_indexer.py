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
        
        TABLE_METADATA = {
            "employees": {
                "description": "Stores personnel data, staff members, workers, team members, managers.",
                "columns": {
                    "id": "Unique identifier for the employee.",
                    "user_code": "Unique alphanumeric code assigned to the user.",
                    "first_name": "Employee's first name.",
                    "last_name": "Employee's last name.",
                    "email": "Contact email address of the employee.",
                    "department_id": "Foreign key to the department the employee belongs to.",
                    "status": "Current employment status (e.g., Active, Inactive)."
                }
            },
            "departments": {
                "description": "Organizational units, business divisions, groups, cost centers.",
                "columns": {
                    "id": "Unique identifier for the department.",
                    "name": "Name of the department (e.g., Engineering, Sales).",
                    "cost_center_code": "Accounting code for allocating costs."
                }
            },
            "projects": {
                "description": "Business initiatives, engagements, assignments, tasks being worked on.",
                "columns": {
                    "id": "Unique identifier for the project.",
                    "name": "Name of the project.",
                    "type": "Type or category of the project.",
                    "status": "Current phase or state of the project.",
                    "department_id": "Department responsible for the project.",
                    "owner_employee_id": "Employee acting as the project manager or owner.",
                    "client_id": "Client that sponsored the project."
                }
            },
            "assignments": {
                "description": "Links employees to projects. Contains project roles, allocation percent, and staffing info.",
                "columns": {
                    "id": "Unique assignment identifier.",
                    "employee_id": "The assigned employee.",
                    "project_id": "The project they are assigned to.",
                    "role": "The specific job title or role on this project.",
                    "allocation_percent": "Percentage of the employee's time dedicated to this project."
                }
            },
            "clients": {
                "description": "Customers, organizations that sponsor projects and receive invoices.",
                "columns": {
                    "id": "Unique client identifier.",
                    "name": "Name of the client organization.",
                    "industry": "Business sector or industry of the client.",
                    "contact_email": "Primary contact email."
                }
            },
            "vendors": {
                "description": "Third-party suppliers, contractors, external companies.",
                "columns": {
                    "id": "Unique vendor identifier.",
                    "name": "Name of the vendor organization.",
                    "service_type": "Type of service or goods provided."
                }
            },
            "invoices": {
                "description": "Billing records, bills, amounts charged to clients for project work.",
                "columns": {
                    "id": "Unique invoice identifier.",
                    "client_id": "The client being billed.",
                    "project_id": "The project the work was performed for.",
                    "amount": "The total monetary value of the invoice.",
                    "status": "Payment status (e.g., Pending, Paid)."
                }
            },
            "project_costs": {
                "description": "Expenses, spending, costs incurred during a project, payments to vendors.",
                "columns": {
                    "id": "Unique cost record identifier.",
                    "project_id": "The project that incurred the cost.",
                    "vendor_id": "The vendor who was paid (if applicable).",
                    "amount": "The monetary value of the cost.",
                    "category": "Classification of the expense."
                }
            },
            "project_revenues": {
                "description": "Income, earnings, money generated from projects paid by clients.",
                "columns": {
                    "id": "Unique revenue record identifier.",
                    "project_id": "The project that generated the revenue.",
                    "client_id": "The client who paid.",
                    "amount": "The monetary value of the revenue."
                }
            },
            "designations": {
                "description": "Job titles, roles, positions, seniority levels of employees.",
                "columns": {
                    "id": "Unique designation identifier.",
                    "name": "Title of the designation (e.g., Senior Engineer)."
                }
            },
            "software_tools": {
                "description": "Applications, software, licenses, tools used by employees.",
                "columns": {
                    "id": "Unique software tool identifier.",
                    "name": "Name of the software (e.g., Photoshop, Jira).",
                    "license_type": "Type of software license."
                }
            }
        }

        for table_name in inspector.get_table_names():
            # Skip some internal tables like alembic_version if they exist
            if table_name == "alembic_version":
                continue
                
            columns = inspector.get_columns(table_name)
            pk = inspector.get_pk_constraint(table_name)
            fks = inspector.get_foreign_keys(table_name)
            
            # Construct a clear description of the table
            desc_lines = [f"Table: {table_name}"]
            
            # Add business description to improve semantic matching
            table_meta = TABLE_METADATA.get(table_name, {})
            if "description" in table_meta:
                desc_lines.append(f"Description: {table_meta['description']}")
                
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
                
                col_desc = ""
                if "columns" in table_meta and col_name in table_meta["columns"]:
                    col_desc = f" - {table_meta['columns'][col_name]}"
                    
                desc_lines.append(f"- {col_name}: {col_type}{is_pk}{fk_str}{col_desc}")
            
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
