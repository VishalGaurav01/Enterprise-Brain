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


# ---------------------------------------------------------------------------
# Curated Tool Registry: The LLM only knows about these intents.
# No OpenAPI parsing. No raw SQL for mutations.
# ---------------------------------------------------------------------------
TOOL_REGISTRY = {
    # ── Employees ──────────────────────────────────────────────────────────
    "update_employee": {
        "description": "Update one or more fields (first_name, last_name, email, status) of an existing employee identified by their name.",
        "needs_lookup": True,
        "lookup_resource": "employees",
        "lookup_name_fields": ["first_name", "last_name"],
        "method": "PATCH",
        "endpoint_template": "/api/v1/employees/{id}",
        "example_payload": {"first_name": "John", "last_name": "Doe", "email": "john@example.com"},
    },
    "delete_employee": {
        "description": "Permanently delete an employee by their name.",
        "needs_lookup": True,
        "lookup_resource": "employees",
        "lookup_name_fields": ["first_name", "last_name"],
        "method": "DELETE",
        "endpoint_template": "/api/v1/employees/{id}",
        "example_payload": {},
    },
    "create_employee": {
        "description": "Create a new employee. Requires first_name, last_name, email, department name (will be looked up), designation name (will be looked up), and optionally status.",
        "needs_lookup": False,
        "method": "POST",
        "endpoint_template": "/api/v1/employees/",
        "example_payload": {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "department_name": "Engineering", "designation_name": "Software Engineer", "status": "active"},
    },
    # ── Projects ───────────────────────────────────────────────────────────
    "update_project": {
        "description": "Update a project's fields (name, status, budget_allocated) by the project's current name. Valid status values: active, planning, completed, on-hold.",
        "needs_lookup": True,
        "lookup_resource": "projects",
        "lookup_name_fields": ["name"],
        "method": "PATCH",
        "endpoint_template": "/api/v1/projects/{id}",
        "example_payload": {"status": "planning"},
    },
    "delete_project": {
        "description": "Delete a project by its name.",
        "needs_lookup": True,
        "lookup_resource": "projects",
        "lookup_name_fields": ["name"],
        "method": "DELETE",
        "endpoint_template": "/api/v1/projects/{id}",
        "example_payload": {},
    },
    "create_project": {
        "description": "Create a new project. Requires name, project_type (fixed-price / time-and-material / retainer), department name, owner employee name, client name.",
        "needs_lookup": False,
        "method": "POST",
        "endpoint_template": "/api/v1/projects/",
        "example_payload": {"name": "Project X", "project_type": "fixed-price", "department_name": "Engineering", "owner_employee_name": "Sarah Connor", "client_name": "Acme Corp"},
    },
    # ── Departments ────────────────────────────────────────────────────────
    "update_department": {
        "description": "Update a department's fields (name, description) by the department's current name.",
        "needs_lookup": True,
        "lookup_resource": "departments",
        "lookup_name_fields": ["name"],
        "method": "PATCH",
        "endpoint_template": "/api/v1/departments/{id}",
        "example_payload": {"name": "New Name"},
    },
    "create_department": {
        "description": "Create a new department. Requires name, description, and cost_center_code.",
        "needs_lookup": False,
        "method": "POST",
        "endpoint_template": "/api/v1/departments/",
        "example_payload": {"name": "Marketing", "description": "Marketing team", "cost_center_code": "CC-MKT-01"},
    },
    # ── Assignments ────────────────────────────────────────────────────────
    "create_assignment": {
        "description": "Assign an employee to a project with a role and allocation percentage. Requires employee name, project name, role, and allocation_percent.",
        "needs_lookup": False,
        "method": "POST",
        "endpoint_template": "/api/v1/assignments/",
        "example_payload": {"employee_name": "Alex Turner", "project_name": "Project Alpha", "role": "Developer", "allocation_percent": 50},
    },
    "delete_assignment": {
        "description": "Remove an employee's assignment from a project. Identify by employee name and project name.",
        "needs_lookup": True,
        "lookup_resource": "assignments",
        "lookup_name_fields": ["employee_id", "project_id"],
        "method": "DELETE",
        "endpoint_template": "/api/v1/assignments/{id}",
        "example_payload": {},
    },
}

TOOL_DESCRIPTIONS_FOR_LLM = "\n".join([
    f'- "{intent}": {cfg["description"]}  |  Example payload: {json.dumps(cfg["example_payload"])}'
    for intent, cfg in TOOL_REGISTRY.items()
])


class ActionAgent:
    def __init__(self, llm, model_id):
        self.llm = llm
        self.model_id = model_id

    async def run_stream(self, query: str, token: str, websocket=None):
        import httpx
        import re
        import time
        from core.database import get_db
        from apps.projectService.service.project import get_all_projects
        from apps.employeeService.service.employee import get_all_employees
        from apps.employeeService.service import department as dept_svc
        from apps.financeService.service import client as client_svc
        from apps.projectService.service import assignment as assign_svc

        BASE_URL = "http://localhost:8000"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

        # Helper: fetch all records from DB directly (no HTTP, no auth)
        def db_get_all(resource: str) -> list:
            db = next(get_db())
            try:
                if resource == "projects":
                    items = get_all_projects(db, skip=0, limit=2000)
                    return [i.model_dump() for i in items]
                elif resource == "employees":
                    items = get_all_employees(db, skip=0, limit=2000)
                    return [i.model_dump() for i in items]
                elif resource == "departments":
                    items = dept_svc.get_all_departments(db, skip=0, limit=500)
                    return [i.model_dump() for i in items]
                elif resource == "clients":
                    items = client_svc.get_all_clients(db, skip=0, limit=500)
                    return [i.model_dump() for i in items]
                elif resource == "assignments":
                    items = assign_svc.get_all_assignments(db, skip=0, limit=2000)
                    return [i.model_dump() for i in items]
                return []
            except Exception as e:
                print(f"[ActionAgent] db_get_all({resource}) error: {e}")
                return []
            finally:
                db.close()

        # Helper: find an entity by fuzzy name match, return its UUID string
        def db_find_by_name(resource: str, name_fields: list, search_name: str) -> str | None:
            items = db_get_all(resource)
            search_lower = search_name.lower()
            for item in items:
                combined = " ".join(str(item.get(f) or "") for f in name_fields).lower()
                if search_lower in combined or combined in search_lower:
                    return str(item.get("id"))
            return None

        # FK resource map: payload key → (resource, name_fields, output_key)
        FK_MAP = {
            "department_name":     ("departments",  ["name"],         "department_id"),
            "designation_name":    ("designations",  ["name"],         "designation_id"),
            "owner_employee_name": ("employees",     ["first_name", "last_name"], "owner_employee_id"),
            "client_name":         ("clients",       ["company_name"], "client_id"),
            "employee_name":       ("employees",     ["first_name", "last_name"], "employee_id"),
            "project_name":        ("projects",      ["name"],         "project_id"),
        }

        yield {"type": "status", "content": "Analyzing your request..."}

        # ── PHASE 1: Intent Parsing ────────────────────────────────────────
        import asyncio
        loop = asyncio.get_event_loop()
        step1_start = time.time()
        system_prompt = f"""You are an API Action Agent for an enterprise system.
The user wants to perform a data modification operation.

Available actions:
{TOOL_DESCRIPTIONS_FOR_LLM}

Analyze the user's request and respond ONLY with a raw JSON object.
Do NOT include markdown, code fences, or any text outside the JSON.

Use exactly this structure:
{{"intent": "update_project", "entity_name": "Project Alpha", "payload": {{"status": "planning"}}, "description": "Update Project Alpha status to planning"}}

Rules:
- "intent" must be one of the action names listed above.
- "entity_name" is the human-readable name of the record to act on (null for create operations).
- "payload" must contain ONLY the fields that need to change or be created.
- For foreign keys use human-readable names: e.g. "department_name": "Engineering" (not an ID).
- "description" is a one-sentence plain English summary of what will happen.
- Output ONLY valid JSON. No extra text before or after.
"""
        try:
            def _intent_call():
                return self.llm.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query},
                    ],
                    model=self.model_id,
                    max_tokens=512,
                    temperature=0.0,
                )
            resp = await loop.run_in_executor(None, _intent_call)
            llm_raw = resp.choices[0].message.content.strip()
        except Exception as e:
            yield {"type": "error", "content": f"LLM error: {str(e)}"}
            return

        # Strip markdown code fences if the model wrapped the JSON
        clean = llm_raw.strip()
        for fence in ["```json", "```JSON", "```"]:
            if clean.startswith(fence):
                clean = clean[len(fence):].strip()
        if clean.endswith("```"):
            clean = clean[:-3].strip()

        # Try direct parse first, then fall back to regex extraction
        parsed = None
        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", clean)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

        if parsed is None:
            yield {
                "type": "error",
                "content": f"I couldn't parse a valid action plan from the LLM response. Raw output:\n\n{llm_raw[:500]}"
            }
            return

        intent = parsed.get("intent")
        entity_name = parsed.get("entity_name")
        payload = parsed.get("payload", {})
        description = parsed.get("description", f"Perform {intent}")
        step1_duration = int((time.time() - step1_start) * 1000)

        if intent not in TOOL_REGISTRY:
            yield {"type": "content", "content": f"I don't know how to perform '{intent}'. Supported: {', '.join(TOOL_REGISTRY.keys())}"}
            return

        tool = TOOL_REGISTRY[intent]
        yield {"type": "step", "title": "Intent Parsed", "content": f"Intent: {intent}\nEntity: {entity_name}\n{description}", "duration_ms": step1_duration}

        # ── PHASE 2: Lookup directly from DB (no HTTP) ────────────────────
        resolved_id = None
        if tool["needs_lookup"] and entity_name:
            yield {"type": "status", "content": f"Looking up '{entity_name}' in database..."}
            step2_start = time.time()
            resource = tool["lookup_resource"]
            name_fields = tool["lookup_name_fields"]
            items, resolved_id = await loop.run_in_executor(
                None,
                lambda: (db_get_all(resource), db_find_by_name(resource, name_fields, entity_name))
            )
            step2_duration = int((time.time() - step2_start) * 1000)
            if not resolved_id:
                yield {
                    "type": "error",
                    "content": f"Could not find '{entity_name}' ({len(items)} {resource} records checked). Please check the exact name."
                }
                return
            yield {"type": "step", "title": "Entity Lookup", "content": f"Found '{entity_name}' → ID: {resolved_id} ({len(items)} records searched)", "duration_ms": step2_duration}

        # Resolve foreign-key names in payload to IDs using direct DB lookup
        final_payload = {}
        for key, val in payload.items():
            if key in FK_MAP:
                resource, name_fields, fk_key = FK_MAP[key]
                fk_id = await loop.run_in_executor(
                    None, lambda r=resource, n=name_fields, v=val: db_find_by_name(r, n, str(v))
                )
                if not fk_id:
                    yield {"type": "error", "content": f"Could not find '{val}' for field '{key}' in {resource}."}
                    return
                final_payload[fk_key] = fk_id
            else:
                final_payload[key] = val

        endpoint = tool["endpoint_template"]
        if resolved_id:
            endpoint = endpoint.replace("{id}", resolved_id)
        method = tool["method"]

        # ── PHASE 3: Confirmation Gate ────────────────────────────────────
        yield {
            "type": "confirm",
            "action_description": description,
            "method": method,
            "endpoint": endpoint,
            "payload": final_payload,
        }

        if websocket is not None:
            try:
                confirm_data = await websocket.receive_json()
                approved = confirm_data.get("approved", False)
            except Exception:
                approved = False
        else:
            approved = False

        if not approved:
            yield {"type": "content", "content": "Action cancelled. No changes were made."}
            return

        # ── PHASE 4: Execute Mutation + Summarize ─────────────────────────
        yield {"type": "status", "content": f"Executing {method} {endpoint}..."}
        step4_start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                url = f"{BASE_URL}{endpoint}"
                if method == "DELETE":
                    api_resp = await client.delete(url, headers=headers)
                elif method == "PATCH":
                    api_resp = await client.patch(url, json=final_payload, headers=headers)
                elif method == "POST":
                    api_resp = await client.post(url, json=final_payload, headers=headers)
                else:
                    api_resp = await client.request(method, url, json=final_payload, headers=headers)
                result_text = api_resp.text
                status_code = api_resp.status_code
        except Exception as e:
            yield {"type": "error", "content": f"API call failed: {str(e)}"}
            return

        step4_duration = int((time.time() - step4_start) * 1000)
        yield {"type": "step", "title": f"{method} {endpoint}", "content": f"HTTP {status_code}\n{result_text}", "duration_ms": step4_duration}

        success = 200 <= status_code < 300
        summary_prompt = (
            f'User asked: "{query}"\n'
            f"Action taken: {description}\n"
            f"API returned HTTP {status_code}: {result_text}\n\n"
            f"Write a short, friendly {'success' if success else 'failure'} message. Be specific. No markdown."
        )
        try:
            def _summary_call():
                return self.llm.chat_completion(
                    messages=[{"role": "user", "content": summary_prompt}],
                    model=self.model_id, max_tokens=256, temperature=0.3,
                )
            sum_resp = await loop.run_in_executor(None, _summary_call)
            final_answer = sum_resp.choices[0].message.content.strip()
        except Exception:
            final_answer = f"{'Done! ' if success else 'Error: '}{description} — HTTP {status_code}"

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
            import asyncio
            loop = asyncio.get_event_loop()

            # 1. Summarization (non-blocking)
            if history:
                yield {
                    "type": "status",
                    "content": "Understanding context from history...",
                }

            step1_start = time.time()
            refined_query = await loop.run_in_executor(
                None, self.summarizer.run, query, history
            )
            step1_duration = int((time.time() - step1_start) * 1000)

            if history:
                yield {
                    "type": "step",
                    "title": "Summarizer Agent (Refined Query)",
                    "content": refined_query,
                    "duration_ms": step1_duration,
                }

            # 2. Retrieval (non-blocking)
            yield {
                "type": "status",
                "content": f"Searching schema and relationships...",
            }

            step2_start = time.time()
            context = await loop.run_in_executor(
                None, self.retrieval.run, refined_query
            )
            step2_duration = int((time.time() - step2_start) * 1000)
            yield {
                "type": "step",
                "title": "Retrieval Agent (Database Context)",
                "content": context,
                "duration_ms": step2_duration,
            }

            # 3. SQL Generation + Execution (non-blocking)
            yield {"type": "status", "content": "Generating and executing SQL..."}

            step3_start = time.time()
            sql_query, sql_result = await loop.run_in_executor(
                None, self.sql_gen.run, refined_query, context
            )
            step3_duration = int((time.time() - step3_start) * 1000)

            yield {"type": "sql", "content": sql_query}
            yield {
                "type": "step",
                "title": "Database Execution Result",
                "content": sql_result,
                "duration_ms": step3_duration,
            }

            # 4. Response Summary — streamed token by token (non-blocking per chunk)
            yield {"type": "status", "content": "Analyzing results and composing answer..."}

            step4_start = time.time()

            def _collect_stream():
                """Run the blocking LLM stream in executor, collect all chunks."""
                chunks = []
                for chunk in self.responder.run_stream(refined_query, sql_query, sql_result):
                    chunks.append(chunk)
                return chunks

            response_chunks = await loop.run_in_executor(None, _collect_stream)

            for chunk in response_chunks:
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
