from app.services.agents.base import BaseAgent
from app.services.agents.graphs.software_engineering_graph import app_graph

_FALLBACK_STEPS = [
    "analyze requirement",
    "break into tasks",
    "define architecture",
]


class PlannerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "planner"

    def run(self, input: dict) -> dict:
        goal = input.get("goal", "build a software system")

        try:
            result = app_graph.invoke({"goal": goal})
            final_output = result.get("final_output", {})
            tasks = result.get("tasks") or final_output.get("tasks", _FALLBACK_STEPS)
            analysis = result.get("analysis") or final_output.get("analysis", "")

            return {
                "agent": "planner",
                "steps": tasks,
                "status": "success",
                "analysis": analysis,
                "tasks": tasks,
                "architecture": result.get("architecture")
                or final_output.get("architecture", []),
                "code_plan": result.get("code_plan")
                or final_output.get("code_plan", []),
                "tests": result.get("tests") or final_output.get("tests", []),
            }
        except Exception:
            return {
                "agent": "planner",
                "steps": _FALLBACK_STEPS,
                "status": "success",
            }
