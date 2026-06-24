from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.services.agents import AgentService

_service = AgentService()


class GraphState(TypedDict, total=False):
    goal: str
    analysis: str
    steps: list[str]
    tasks: list[str]
    architecture: list[str]
    code_plan: list[str]
    tests: list[str]
    final_output: dict


def analyze_node(state: GraphState) -> GraphState:
    goal = state.get("goal", "build a software system")
    result = _service.run("planner", {"goal": goal})
    return {
        "analysis": result.get("analysis"),
        "steps": result.get("steps"),
        "tasks": result.get("tasks"),
    }


def architect_node(state: GraphState) -> GraphState:
    goal = state.get("goal", "build a software system")
    result = _service.run("architect", {"goal": goal})
    return {"architecture": result.get("architecture", [])}


def developer_node(state: GraphState) -> GraphState:
    goal = state.get("goal", "build a software system")
    result = _service.run(
        "developer",
        {
            "goal": goal,
            "architecture": state.get("architecture"),
        },
    )
    return {"code_plan": result.get("code_plan", [])}


def qa_node(state: GraphState) -> GraphState:
    goal = state.get("goal", "build a software system")
    result = _service.run(
        "qa",
        {
            "goal": goal,
            "code_plan": state.get("code_plan"),
        },
    )
    return {"tests": result.get("tests", [])}


def finalize_node(state: GraphState) -> GraphState:
    return {
        "final_output": {
            "analysis": state.get("analysis"),
            "steps": state.get("steps"),
            "architecture": state.get("architecture"),
            "code_plan": state.get("code_plan"),
            "tests": state.get("tests"),
        },
    }


def _build_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("analyze_node", analyze_node)
    graph.add_node("architect_node", architect_node)
    graph.add_node("developer_node", developer_node)
    graph.add_node("qa_node", qa_node)
    graph.add_node("finalize_node", finalize_node)
    graph.add_edge(START, "analyze_node")
    graph.add_edge("analyze_node", "architect_node")
    graph.add_edge("architect_node", "developer_node")
    graph.add_edge("developer_node", "qa_node")
    graph.add_edge("qa_node", "finalize_node")
    graph.add_edge("finalize_node", END)
    return graph


app_graph = _build_graph().compile()
