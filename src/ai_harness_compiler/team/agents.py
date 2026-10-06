"""Bounded tool-using agents with interchangeable local and Ollama decision policies."""

import json
from typing import Protocol

import httpx

from ai_harness_compiler.models.team import AgentDecision, AgentReport, Persona, ToolResult
from ai_harness_compiler.team.personas import system_prompt
from ai_harness_compiler.team.tools import TeamTools


class DecisionPolicy(Protocol):
    def decide(
        self, persona: Persona, request: str, observations: list[ToolResult]
    ) -> AgentDecision: ...


class LocalPolicy:
    def decide(
        self, persona: Persona, request: str, observations: list[ToolResult]
    ) -> AgentDecision:
        used = {item.tool for item in observations}
        if "retrieve_context" not in used:
            return AgentDecision(
                action="tool",
                tool="retrieve_context",
                query=f"{request} {persona.objective}"[:1000],
            )
        if "retrieve_memory" not in used:
            return AgentDecision(
                action="tool",
                tool="retrieve_memory",
                query=f"{request} {persona.objective}"[:1000],
            )
        if persona.required_tool not in used:
            return AgentDecision(action="tool", tool=persona.required_tool)
        warnings = sum(len(item.findings) for item in observations)
        return AgentDecision(
            action="finish",
            summary=(
                f"{persona.name}: {observations[-1].summary} "
                f"{warnings} findings recorded for review. Product acceptance remains with the PO."
            ),
        )


class OllamaPolicy:
    def __init__(self, model: str, client: httpx.Client | None = None) -> None:
        self.model = model
        self.client = client

    def decide(
        self, persona: Persona, request: str, observations: list[ToolResult]
    ) -> AgentDecision:
        bounded_observations = []
        for observation in observations:
            data = observation.model_dump()
            if len(json.dumps(data, ensure_ascii=False)) > 16000:
                data = {
                    "tool": observation.tool,
                    "summary": observation.summary,
                    "findings": [finding.model_dump() for finding in observation.findings[:20]],
                    "omitted_data_keys": list(observation.data),
                    "omitted_for_context_budget": True,
                }
            bounded_observations.append(data)
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": AgentDecision.model_json_schema(),
            "options": {"temperature": 0, "num_predict": 1200},
            "messages": [
                {"role": "system", "content": system_prompt(persona)},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "request": request,
                            "available_tools": persona.tools,
                            "observations": bounded_observations,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        if self.client is None:
            with httpx.Client(timeout=30, trust_env=False) as client:
                response = client.post("http://127.0.0.1:11434/api/chat", json=payload)
        else:
            response = self.client.post("http://127.0.0.1:11434/api/chat", json=payload)
        response.raise_for_status()
        return AgentDecision.model_validate_json(response.json()["message"]["content"])


class BoundedAgent:
    def __init__(
        self, persona: Persona, tools: TeamTools, policy: DecisionPolicy, max_steps: int = 5
    ) -> None:
        self.persona, self.tools, self.policy, self.max_steps = persona, tools, policy, max_steps

    def run(self, request: str, engine: str) -> AgentReport:
        observations: list[ToolResult] = []
        try:
            for _ in range(self.max_steps):
                decision = self.policy.decide(self.persona, request, observations)
                if decision.action == "finish":
                    used = {item.tool for item in observations}
                    if not {
                        "retrieve_context",
                        "retrieve_memory",
                        self.persona.required_tool,
                    }.issubset(used):
                        raise ValueError("Agent cannot finish before its required evidence tools")
                    return AgentReport.model_validate(
                        {
                            "agent_id": self.persona.id,
                            "status": "completed",
                            "engine": engine,
                            "summary": decision.summary,
                            "observations": [item.model_dump() for item in observations],
                            "model_summary_is_advisory": engine == "ollama",
                        }
                    )
                if decision.tool is None or decision.tool not in self.persona.tools:
                    raise ValueError("Tool denied by agent permission policy")
                observations.append(self.tools.call(decision.tool, decision.query))
            raise RuntimeError("Agent step budget exhausted")
        except (ValueError, RuntimeError, httpx.HTTPError, KeyError, TypeError, SyntaxError) as exc:
            return AgentReport.model_validate(
                {
                    "agent_id": self.persona.id,
                    "status": "failed",
                    "engine": engine,
                    "summary": f"Agent stopped: {type(exc).__name__}: {str(exc)[:300]}",
                    "observations": [item.model_dump() for item in observations],
                }
            )
