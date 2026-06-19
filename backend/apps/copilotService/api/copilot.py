import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from apps.copilotService.service.agent import CopilotAgent
from apps.shared.security import verify_token

router = APIRouter()
agent = None

def get_agent():
    global agent
    if agent is None:
        agent = CopilotAgent()
    return agent

class CopilotQuery(BaseModel):
    query: str
    history: list[dict] = []

class CopilotResponse(BaseModel):
    query: str
    sql_generated: str
    response: str
    context_used: list[str]

@router.post("/query", response_model=CopilotResponse, dependencies=[Depends(verify_token)])
def ask_copilot(payload: CopilotQuery):
    result = get_agent().run(payload.query, payload.history)
    return CopilotResponse(**result)

@router.websocket("/ws/query")
async def copilot_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            token = payload.get("token")
            if not token:
                await websocket.send_text(json.dumps({"type": "error", "content": "Authentication failed"}))
                await websocket.close()
                break

            query = payload.get("query")
            history = payload.get("history", [])
            mode = payload.get("mode", "READ")
            if not query:
                continue

            copilot = get_agent()

            if mode == "ACTION":
                # In ACTION mode, we stream events and pause for confirmation.
                # The action_agent.run_stream will yield a "confirm" event,
                # then wait for the next WebSocket message (approve/cancel).
                async for chunk in copilot.action_agent.run_stream(query, token, websocket=websocket):
                    await websocket.send_text(json.dumps(chunk))
                    # If we just sent the confirm event, the agent is now suspended
                    # waiting for websocket.receive_json() internally — nothing to do here.

                import time
                total_ms = 0  # duration tracked internally
                await websocket.send_text(json.dumps({"type": "done", "total_duration_ms": total_ms}))
            else:
                async for chunk in copilot.run_stream(query, history, mode, token):
                    await websocket.send_text(json.dumps(chunk))

    except WebSocketDisconnect:
        print("Copilot WebSocket disconnected")
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))
        except Exception:
            pass

