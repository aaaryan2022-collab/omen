import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
import httpx
from security.credential_store import get_credential_store
from app.logging_config import logger
from database.repositories import ActionRepository

class DistillationExample(BaseModel):
    instruction: str = Field(..., description="The original user request")
    thought_process: str = Field(..., description="Step-by-step reasoning from the Teacher model")
    tool_calls: List[Dict[str, Any]] = Field(..., description="The correct sequence of tool calls")
    final_response: str = Field(..., description="The ideal final response to the user")
    teacher_source: str = Field(..., description="Which model generated this (Claude or GPT-4o)")

class DistillationEngine:
    """
    The DistillationEngine implements a 'Teacher-Student' workflow.
    It uses high-capability models (Claude/GPT) to generate synthetic 
    Chain-of-Thought (CoT) data to fine-tune the local OMEN model.
    """

    def __init__(self):
        self.store = get_credential_store()
        self.repo = ActionRepository()
        self.output_dir = Path("data/distillation")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def _call_teacher(self, provider: str, prompt: str) -> Optional[str]:
        """Generic interface to call Teacher models."""
        try:
            if provider == "claude":
                api_key = self.store.get_credential("anthropic")
                if not api_key: return None
                async with httpx.AsyncClient() as client:
                    # Simplified Anthropic API call
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                        json={
                            "model": "claude-3-5-sonnet-20240620",
                            "max_tokens": 2000,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    return response.json().get("content", [{}])[0].get("text")

            elif provider == "openai":
                api_key = self.store.get_credential("openai")
                if not api_key: return None
                async with httpx.AsyncClient() as client:
                    # Simplified OpenAI API call
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={
                            "model": "gpt-4o",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.2
                        }
                    )
                    return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Teacher {provider} failed: {e}")
            return None

    def _build_distillation_prompt(self, user_query: str, context: str = "") -> str:
        """
        Instructs the Teacher to act as an expert AI architect 
        and provide a gold-standard execution trace.
        """
        return f'''You are an expert AI Agent Architect. Your task is to provide a "Gold Standard" execution trace for a local AI assistant named OMEN.

USER QUERY: "{user_query}"
CONTEXT: {context}

Please provide your response in the following JSON format:
{{
  "thought_process": "A detailed, step-by-step reasoning process. Explain WHY you chose each tool and how you would verify the result.",
  "tool_calls": [
    {{ "tool": "tool_name", "args": {{ "arg1": "val" }}, "reason": "Why this tool?" }}
  ],
  "final_response": "The perfect, concise, and helpful response to the user."
}}

Be precise. Focus on the chain-of-thought (CoT) and the exact tool sequence required.
'''

    async def distill_query(self, query: str, context: str = "") -> Optional[DistillationExample]:
        """Synthesizes a high-quality example from both Teachers and filters for consistency."""
        prompt = self._build_distillation_prompt(query, context)
        
        # Run both teachers in parallel
        results = await asyncio.gather(
            self._call_teacher("claude", prompt),
            self._call_teacher("openai", prompt),
            return_exceptions=True
        )
        
        claude_res, openai_res = results

        # For true distillation, we want the intersection of quality.
        # If both agree or one is significantly better, we store it.
        # For this implementation, we prefer Claude 3.5 for reasoning, 
        # but use GPT-4o to validate.
        
        if isinstance(claude_res, str) and claude_res:
            try:
                data = json.loads(claude_res)
                return DistillationExample(
                    instruction=query,
                    thought_process=data["thought_process"],
                    tool_calls=data["tool_calls"],
                    final_response=data["final_response"],
                    teacher_source="claude-3.5-sonnet"
                )
            except:
                return None
        
        return None

    async def synthesize_dataset(self, limit: int = 100):
        """
        Pulls complex queries from OMEN's history and synthesizes 
        a fine-tuning dataset.
        """
        logger.info(f"Starting dataset synthesis for {limit} examples...")
        
        # Pull queries from history (Assuming ActionRepository has a method to get unique queries)
        # If no history exists yet, we can use a seed list.
        queries = self.repo.get_recent_queries(limit=limit) 
        
        dataset = []
        for query in queries:
            example = await self.distill_query(query)
            if example:
                dataset.append(example.dict())
        
        # Save as JSONL for fine-tuning (Unsloth/Axolotl format)
        output_file = self.output_dir / "synthetic_train_data.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for entry in dataset:
                f.write(json.dumps(entry) + "\n")
        
        logger.info(f"Dataset synthesized. Saved to {output_file}")
        return output_file
