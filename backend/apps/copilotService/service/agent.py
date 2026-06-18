import os
import json
from sqlalchemy import create_engine, text
# pyrefly: ignore [missing-import]
from langchain_core.prompts import PromptTemplate
# pyrefly: ignore [missing-import]
from huggingface_hub import InferenceClient
from neo4j import GraphDatabase
from apps.copilotService.service.schema_indexer import SchemaIndexer

class SummarizerAgent:
    def __init__(self, llm, model_id):
        self.llm = llm
        self.model_id = model_id

    def run(self, query: str, history: list) -> str:
        if not history:
            return query
        
        # Format history string
        history_str = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in history[-5:]]) # limit to last 5
        messages = [
            {"role": "system", "content": "You are a Query Summarizer Agent. Given a chat history and the latest user query, rewrite the query to be a standalone, self-contained question that can be understood without the history. If the query does not depend on history, return it as is. Return ONLY the refined query string, nothing else."},
            {"role": "user", "content": f"Chat History:\n{history_str}\n\nLatest Query: {query}"}
        ]
        
        response = self.llm.chat_completion(messages=messages, model=self.model_id, max_tokens=100, temperature=0.1)
        refined = response.choices[0].message.content.strip()
        return refined if refined else query

class RetrievalAgent:
    def __init__(self, schema_indexer):
        self.schema_indexer = schema_indexer
        
        # Neo4j setup
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_pass = os.getenv("NEO4J_PASSWORD", "password")
        try:
            self.neo4j_driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_pass))
        except Exception as e:
            print(f"RetrievalAgent: Neo4j not connected - {e}")
            self.neo4j_driver = None

    def _get_neo4j_schema(self):
        if not self.neo4j_driver:
            return "No graph relationships available."
        try:
            with self.neo4j_driver.session() as session:
                # Query db.schema.visualization directly for a simple topology
                result = session.run("CALL db.schema.visualization()")
                data = result.data()
                if not data:
                    return "No graph relationships available."
                
                rels = data[0]['relationships']
                
                context = "Graph Relationships (Nodes and Edges):\n"
                for rel in rels:
                    start = dict(rel.start_node).get('name', 'Unknown')
                    end = dict(rel.end_node).get('name', 'Unknown')
                    type_ = rel.type
                    context += f"- (Table: {start}) --[{type_}]--> (Table: {end})\n"
                return context
        except Exception as e:
            return f"Error retrieving graph schema: {str(e)}"

    def run(self, refined_query: str) -> str:
        # 1. Semantic Search
        relevant_schemas = self.schema_indexer.search_schema(refined_query, k=5)
        schema_context = "Table Schemas:\n" + "\n\n".join(relevant_schemas)
        
        # 2. Graph DB Search
        graph_context = self._get_neo4j_schema()
        
        return f"{schema_context}\n\n{graph_context}"

class SQLGeneratorAgent:
    def __init__(self, llm, model_id, db_url):
        self.llm = llm
        self.model_id = model_id
        self.engine = create_engine(db_url)

    def run(self, refined_query: str, context: str):
        messages = [
            {"role": "system", "content": "You are a PostgreSQL expert database assistant. Your job is to translate the user's question into a syntactically correct PostgreSQL query.\nUse the provided database context (table schemas and graph relationships) to construct your query.\nReturn ONLY the SQL query, nothing else. Do not wrap it in markdown code blocks like ```sql. Just the raw SQL string."},
            {"role": "user", "content": f"Database Context:\n{context}\n\nQuestion:\n{refined_query}"}
        ]
        response = self.llm.chat_completion(messages=messages, model=self.model_id, max_tokens=512, temperature=0.1)
        generated_sql = response.choices[0].message.content.strip()
        
        # Clean up the output if the model added markdown blocks
        if generated_sql.startswith("```sql"):
            generated_sql = generated_sql[6:]
        if generated_sql.startswith("```"):
            generated_sql = generated_sql[3:]
        if generated_sql.endswith("```"):
            generated_sql = generated_sql[:-3]
        generated_sql = generated_sql.strip()

        # Execute
        sql_result_str = ""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(generated_sql))
                rows = result.fetchall()
                sql_result_str = str(rows)
        except Exception as e:
            sql_result_str = f"Error executing query: {str(e)}"
            
        return generated_sql, sql_result_str

class ResponseSummaryAgent:
    def __init__(self, llm, model_id):
        self.llm = llm
        self.model_id = model_id

    def run_stream(self, refined_query: str, sql_query: str, sql_result: str):
        messages = [
            {"role": "system", "content": "You are a helpful AI data analyst. You are given a user question, the SQL query used to find the answer, and the raw result from the database.\nProvide a natural language summary answering the user's question based on the database result. Be concise, professional, and clear. Do NOT say 'The result is...'. Just answer directly."},
            {"role": "user", "content": f"User Question: {refined_query}\n\nSQL Query Used: {sql_query}\n\nDatabase Result: {sql_result}"}
        ]
        for chunk in self.llm.chat_completion(messages=messages, model=self.model_id, max_tokens=512, temperature=0.3, stream=True):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

class CopilotAgent:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            print("WARNING: HUGGINGFACE_API_KEY is not set.")

        self.model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
        try:
            self.llm = InferenceClient(api_key=self.api_key)
        except Exception as e:
            print(f"Failed to initialize LLM: {e}")
            self.llm = None
            
        self.db_url = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@db:5432/brain")
        chroma_host = os.getenv("CHROMA_HOST", "brain_chromadb")
        self.schema_indexer = SchemaIndexer(db_url=self.db_url, chroma_url=chroma_host, chroma_port=8000)
        
        # Initialize sub-agents
        self.summarizer = SummarizerAgent(self.llm, self.model_id)
        self.retrieval = RetrievalAgent(self.schema_indexer)
        self.sql_gen = SQLGeneratorAgent(self.llm, self.model_id, self.db_url)
        self.responder = ResponseSummaryAgent(self.llm, self.model_id)

    def run(self, query: str, history: list = []) -> dict:
        if not self.llm:
            return {"query": query, "sql_generated": "", "response": "LLM is not configured properly.", "context_used": []}
        
        try:
            refined_query = self.summarizer.run(query, history)
            context = self.retrieval.run(refined_query)
            sql_query, sql_result = self.sql_gen.run(refined_query, context)
            
            final_answer = ""
            for chunk in self.responder.run_stream(refined_query, sql_query, sql_result):
                final_answer += chunk
                
            return {
                "query": refined_query,
                "sql_generated": sql_query,
                "response": final_answer.strip(),
                "context_used": [context]
            }
        except Exception as e:
            return {"query": query, "sql_generated": "", "response": f"Error: {str(e)}", "context_used": []}

    async def run_stream(self, query: str, history: list = []):
        if not self.llm:
            yield {"type": "error", "content": "LLM is not configured properly."}
            return

        try:
            # 1. Summarization
            if history:
                yield {"type": "status", "content": "Understanding context from history..."}
            refined_query = self.summarizer.run(query, history)
            if history:
                yield {"type": "step", "title": "Summarizer Agent (Refined Query)", "content": refined_query}
            
            # 2. Retrieval
            yield {"type": "status", "content": f"Searching schema and relationships for: {refined_query}..."}
            context = self.retrieval.run(refined_query)
            yield {"type": "step", "title": "Retrieval Agent (Database Context)", "content": context}
            
            # 3. SQL Generation
            yield {"type": "status", "content": "Generating and executing SQL..."}
            sql_query, sql_result = self.sql_gen.run(refined_query, context)
            yield {"type": "sql", "content": sql_query}
            yield {"type": "step", "title": "Database Execution Result", "content": sql_result}
            
            # 4. Response Summary
            yield {"type": "status", "content": "Analyzing results..."}
            for chunk in self.responder.run_stream(refined_query, sql_query, sql_result):
                yield {"type": "content", "content": chunk}
                
            yield {"type": "done"}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield {"type": "error", "content": f"An error occurred: {str(e)}"}
