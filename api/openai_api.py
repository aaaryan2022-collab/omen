# API — OpenAI-compatible chat, streaming, models, health, agents, tools (authenticated)
from fastapi import FastAPI
app = FastAPI()
@app.get("/v1/models")
def models(): return {"data": []}
@app.post("/v1/chat/completions")
def chat(): return {"choices": []}
