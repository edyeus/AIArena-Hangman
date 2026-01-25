from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Trip Planner API")


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    return {
        "reply": "Thanks for the idea! We'll use this to refine your trip plan.",
        "echo": request.message,
    }
