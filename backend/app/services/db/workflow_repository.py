import logging
from typing import Any

from supabase import Client

from app.services.db.supabase_client import supabase_client

logger = logging.getLogger("app")

AGENT_SEQUENCE = ("planner", "architect", "developer", "qa")


def _agent_runs_from_state(goal: str, state: dict[str, Any]) -> list[dict[str, Any]]:
    architecture = state.get("architecture", [])
    code_plan = state.get("code_plan", [])

    return [
        {
            "agent_name": "planner",
            "input": {"goal": goal},
            "output": {
                "agent": "planner",
                "analysis": state.get("analysis"),
                "steps": state.get("steps", []),
                "tasks": state.get("tasks", []),
                "status": "success",
            },
        },
        {
            "agent_name": "architect",
            "input": {"goal": goal},
            "output": {
                "agent": "architect",
                "architecture": architecture,
                "status": "success",
            },
        },
        {
            "agent_name": "developer",
            "input": {"goal": goal, "architecture": architecture},
            "output": {
                "agent": "developer",
                "code_plan": code_plan,
                "status": "success",
            },
        },
        {
            "agent_name": "qa",
            "input": {"goal": goal, "code_plan": code_plan},
            "output": {
                "agent": "qa",
                "tests": state.get("tests", []),
                "status": "success",
            },
        },
    ]


class WorkflowRepository:
    def __init__(self, client: Client | None = None) -> None:
        self._client = client if client is not None else supabase_client

    def persist_workflow_run(
        self,
        goal: str,
        graph_state: dict[str, Any],
        status: str = "success",
    ) -> str | None:
        if self._client is None:
            logger.warning("Supabase client unavailable; skipping workflow persistence")
            return None

        final_output = graph_state.get("final_output")
        if final_output is None:
            final_output = {
                "analysis": graph_state.get("analysis"),
                "steps": graph_state.get("steps"),
                "architecture": graph_state.get("architecture"),
                "code_plan": graph_state.get("code_plan"),
                "tests": graph_state.get("tests"),
            }

        try:
            workflow_response = (
                self._client.table("workflow_runs")
                .insert(
                    {
                        "goal": goal,
                        "status": status,
                        "final_output": final_output,
                    }
                )
                .execute()
            )
            workflow_id = workflow_response.data[0]["id"]

            agent_rows = [
                {
                    "workflow_id": workflow_id,
                    **agent_run,
                }
                for agent_run in _agent_runs_from_state(goal, graph_state)
            ]
            self._client.table("agent_runs").insert(agent_rows).execute()

            logger.info("Persisted workflow run %s with %d agent runs", workflow_id, len(agent_rows))
            return workflow_id
        except Exception:
            logger.exception("Failed to persist workflow run to Supabase")
            return None
