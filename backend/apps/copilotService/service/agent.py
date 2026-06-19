import os
import json
from sqlalchemy import create_engine, text

# pyrefly: ignore [missing-import]
from langchain_core.prompts import PromptTemplate

# pyrefly: ignore [missing-import]
from huggingface_hub import InferenceClient
from neo4j import GraphDatabase
from apps.copilotService.service.schema_indexer import SchemaIndexer
import concurrent.futures


class SummarizerAgent:
    def __init__(self, llm, model_id):
        self.llm = llm
        self.model_id = model_id

    def run(self, query: str, history: list) -> str:
        if not history:
            return query

        # Format history string
        history_str = "\n".join(
            [
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in history[-5:]
            ]
        )  # limit to last 5
        messages = [
            {
                "role": "system",
                "content": "You are a Query Summarizer Agent. Given a chat history and the latest user query, rewrite the query to be a standalone, self-contained question that can be understood without the history. If the query does not depend on history, return it as is. Return ONLY the refined query string, nothing else.",
            },
            {
                "role": "user",
                "content": f"Chat History:\n{history_str}\n\nLatest Query: {query}",
            },
        ]

        response = self.llm.chat_completion(
            messages=messages, model=self.model_id, max_tokens=100, temperature=0.1
        )
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
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_pass)
            )
        except Exception as e:
            print(f"RetrievalAgent: Neo4j not connected - {e}")
            self.neo4j_driver = None

    def _get_neo4j_schema(self):
        if not self.neo4j_driver:
            return "No graph relationships available."
        try:
            with self.neo4j_driver.session() as session:
                record = session.run("CALL db.schema.visualization()").single()
                if not record or not record.get("relationships"):
                    return "No graph relationships available."

                rels = record["relationships"]

                context = "Graph Relationships (Nodes and Edges):\n"
                for rel in rels:
                    start = (
                        list(rel.nodes[0].labels)[0]
                        if rel.nodes[0].labels
                        else "Unknown"
                    )
                    end = (
                        list(rel.nodes[1].labels)[0]
                        if rel.nodes[1].labels
                        else "Unknown"
                    )
                    type_ = rel.type
                    context += f"- (Table: {start}) --[{type_}]--> (Table: {end})\n"
                return context
        except Exception as e:
            return f"Error retrieving graph schema: {str(e)}"

    def run(self, refined_query: str) -> str:

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Run Semantic Search and Graph DB Search in parallel
            future_schema = executor.submit(
                self.schema_indexer.search_schema, refined_query, 5
            )
            future_graph = executor.submit(self._get_neo4j_schema)

            relevant_schemas = future_schema.result()
            graph_context = future_graph.result()

        schema_context = "Table Schemas:\n" + "\n\n".join(relevant_schemas)

        return f"{schema_context}\n\n{graph_context}"


class SQLGeneratorAgent:
    def __init__(self, llm, model_id, db_url):
        self.llm = llm
        self.model_id = model_id
        self.engine = create_engine(db_url)

    def run(self, refined_query: str, context: str):
        messages = [
            {
                "role": "system",
                "content": "You are a PostgreSQL expert database assistant. Your job is to translate the user's question into a syntactically correct PostgreSQL query.\nUse the provided database context (table schemas and graph relationships) to construct your query.\nReturn ONLY the SQL query, nothing else. Do not wrap it in markdown code blocks like ```sql. Just the raw SQL string.",
            },
            {
                "role": "user",
                "content": f"Database Context:\n{context}\n\nQuestion:\n{refined_query}",
            },
        ]
        response = self.llm.chat_completion(
            messages=messages, model=self.model_id, max_tokens=512, temperature=0.1
        )
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
            {
                "role": "system",
                "content": "You are a helpful AI data analyst. You are given a user question, the SQL query used to find the answer, and the raw result from the database.\nProvide a natural language summary answering the user's question based on the database result. Be concise, professional, and clear. Do NOT say 'The result is...'. Just answer directly.",
            },
            {
                "role": "user",
                "content": f"User Question: {refined_query}\n\nSQL Query Used: {sql_query}\n\nDatabase Result: {sql_result}",
            },
        ]
        for chunk in self.llm.chat_completion(
            messages=messages,
            model=self.model_id,
            max_tokens=512,
            temperature=0.3,
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class ActionAgent:
    def __init__(self, llm, model_id):
        self.llm = llm
        self.model_id = model_id

    async def run_stream(self, query: str, token: str):
        import httpx
        import json
        import re
        import time

        yield {"type": "status", "content": "Initializing Action Mode..."}

        step1_start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/openapi.json")
                if response.status_code != 200:
                    yield {
                        "type": "error",
                        "content": "Could not fetch API definitions.",
                    }
                    return
                openapi_spec = response.json()
        except Exception as e:
            yield {"type": "error", "content": f"Error fetching OpenAPI spec: {str(e)}"}
            return

        paths = openapi_spec.get("paths", {})
        available_tools = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ["post", "put", "delete", "patch"]:
                    tool = {
                        "name": f"{method.upper()} {path}",
                        "description": details.get("summary", ""),
                        "parameters": details.get("requestBody", {}),
                    }
                    available_tools.append(tool)

        tools_str = json.dumps(available_tools, indent=2)
        step1_duration = int((time.time() - step1_start) * 1000)
        yield {
            "type": "step",
            "title": "API Discovery",
            "content": f"Discovered {len(available_tools)} actionable APIs.",
            "duration_ms": step1_duration,
        }

        yield {"type": "status", "content": "Determining action..."}
        step2_start = time.time()

        system_prompt = f"""You are an API Action Agent.
Your job is to read the user's request and determine which API to call.
Here are the available APIs:
{tools_str}

Respond strictly with a JSON object in this format:
{{
  "endpoint": "/api/v1/some/path",
  "method": "POST",
  "payload": {{"key": "value"}}
}}
If no API matches the request, respond with an empty endpoint.
Do not wrap the JSON in markdown blocks. Return raw JSON.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        response = self.llm.chat_completion(
            messages=messages, model=self.model_id, max_tokens=1024, temperature=0.1
        )
        llm_output = response.choices[0].message.content.strip()

        match = re.search(r"\{[\s\S]*\}", llm_output)
        if not match:
            yield {
                "type": "error",
                "content": "I couldn't figure out which API to call.",
            }
            return

        action_data = json.loads(match.group(0))
        endpoint = action_data.get("endpoint")
        method = action_data.get("method", "POST")
        payload = action_data.get("payload", {})

        step2_duration = int((time.time() - step2_start) * 1000)
        yield {
            "type": "step",
            "title": "Action Agent",
            "content": f"Calling {method} {endpoint}\nPayload: {json.dumps(payload, indent=2)}",
            "duration_ms": step2_duration,
        }

        if not endpoint:
            yield {
                "type": "content",
                "content": "I couldn't find an appropriate action for your request.",
            }
            return

        yield {"type": "status", "content": "Executing API request..."}
        step3_start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
                url = f"http://localhost:8000{endpoint}"
                api_resp = await client.request(
                    method, url, json=payload, headers=headers
                )
                result_text = api_resp.text
                status_code = api_resp.status_code
        except Exception as e:
            result_text = str(e)
            status_code = 500

        step3_duration = int((time.time() - step3_start) * 1000)
        yield {
            "type": "step",
            "title": "API Execution Result",
            "content": f"Status: {status_code}\nResponse: {result_text}",
            "duration_ms": step3_duration,
        }

        yield {"type": "status", "content": "Summarizing result..."}
        step4_start = time.time()

        summary_prompt = f"The user wanted to: {query}\nI executed an API call to {endpoint} which returned status {status_code} and response: {result_text}\nSummarize this to the user in a friendly way."

        response = self.llm.chat_completion(
            messages=[{"role": "user", "content": summary_prompt}],
            model=self.model_id,
            max_tokens=512,
            temperature=0.3,
        )
        final_answer = response.choices[0].message.content
        yield {"type": "content", "content": final_answer}


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

        self.db_url = os.getenv(
            "POSTGRES_URL", "postgresql://postgres:postgres@db:5432/brain"
        )
        chroma_host = os.getenv("CHROMA_HOST", "brain_chromadb")
        self.schema_indexer = SchemaIndexer(
            db_url=self.db_url, chroma_url=chroma_host, chroma_port=8000
        )

        # Initialize sub-agents
        self.summarizer = SummarizerAgent(self.llm, self.model_id)
        self.retrieval = RetrievalAgent(self.schema_indexer)
        self.sql_gen = SQLGeneratorAgent(self.llm, self.model_id, self.db_url)
        self.responder = ResponseSummaryAgent(self.llm, self.model_id)
        self.action_agent = ActionAgent(self.llm, self.model_id)

    def run(self, query: str, history: list = []) -> dict:
        if not self.llm:
            return {
                "query": query,
                "sql_generated": "",
                "response": "LLM is not configured properly.",
                "context_used": [],
            }

        try:
            refined_query = self.summarizer.run(query, history)
            context = self.retrieval.run(refined_query)
            sql_query, sql_result = self.sql_gen.run(refined_query, context)

            final_answer = ""
            for chunk in self.responder.run_stream(
                refined_query, sql_query, sql_result
            ):
                final_answer += chunk

            return {
                "query": refined_query,
                "sql_generated": sql_query,
                "response": final_answer.strip(),
                "context_used": [context],
            }
        except Exception as e:
            return {
                "query": query,
                "sql_generated": "",
                "response": f"Error: {str(e)}",
                "context_used": [],
            }

    async def run_stream(
        self, query: str, history: list = [], mode: str = "READ", token: str = ""
    ):
        if not self.llm:
            yield {"type": "error", "content": "LLM is not configured properly."}
            return

        import time

        start_time = time.time()

        if mode == "ACTION":
            try:
                async for chunk in self.action_agent.run_stream(query, token):
                    yield chunk
                total_duration = int((time.time() - start_time) * 1000)
                yield {"type": "done", "total_duration_ms": total_duration}
            except Exception as e:
                import traceback

                traceback.print_exc()
                yield {"type": "error", "content": f"An error occurred: {str(e)}"}
            return

        try:
            # 1. Summarization
            if history:
                yield {
                    "type": "status",
                    "content": "Understanding context from history...",
                }

            step1_start = time.time()
            refined_query = self.summarizer.run(query, history)
            step1_duration = int((time.time() - step1_start) * 1000)

            if history:
                yield {
                    "type": "step",
                    "title": "Summarizer Agent (Refined Query)",
                    "content": refined_query,
                    "duration_ms": step1_duration,
                }

            # 2. Retrieval
            yield {
                "type": "status",
                "content": f"Searching schema and relationships for: {refined_query}...",
            }

            step2_start = time.time()
            context = self.retrieval.run(refined_query)
            step2_duration = int((time.time() - step2_start) * 1000)
            yield {
                "type": "step",
                "title": "Retrieval Agent (Database Context)",
                "content": context,
                "duration_ms": step2_duration,
            }

            # 3. SQL Generation
            yield {"type": "status", "content": "Generating and executing SQL..."}

            step3_start = time.time()
            sql_query, sql_result = self.sql_gen.run(refined_query, context)
            step3_duration = int((time.time() - step3_start) * 1000)

            yield {"type": "sql", "content": sql_query}
            yield {
                "type": "step",
                "title": "Database Execution Result",
                "content": sql_result,
                "duration_ms": step3_duration,
            }

            # 4. Response Summary
            yield {"type": "status", "content": "Analyzing results..."}

            step4_start = time.time()
            for chunk in self.responder.run_stream(
                refined_query, sql_query, sql_result
            ):
                yield {"type": "content", "content": chunk}
            step4_duration = int((time.time() - step4_start) * 1000)
            yield {
                "type": "step",
                "title": "Response Summary Agent",
                "content": "Response streamed successfully.",
                "duration_ms": step4_duration,
            }

            total_duration = int((time.time() - start_time) * 1000)
            yield {"type": "done", "total_duration_ms": total_duration}

        except Exception as e:
            import traceback

            traceback.print_exc()
            yield {"type": "error", "content": f"An error occurred: {str(e)}"}
