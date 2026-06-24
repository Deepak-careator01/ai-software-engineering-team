from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.services.agents.architect_agent import ArchitectAgent
from app.services.agents.developer_agent import DeveloperAgent
from app.services.agents.qa_agent import QAAgent

_architect_agent = ArchitectAgent()
_developer_agent = DeveloperAgent()
_qa_agent = QAAgent()


class GraphState(TypedDict, total=False):
    goal: str
    analysis: str
    tasks: list[str]
    architecture: list[str]
    code_plan: list[str]
    tests: list[str]
    final_output: dict


def analyze_node(state: GraphState) -> GraphState:
    goal = state.get("goal", "build a software system")
    return {
        "analysis": f"Analyzed requirement for goal: {goal}",
    }


def breakdown_node(state: GraphState) -> GraphState:
    analysis = state.get("analysis", "")
    return {
        "tasks": [
            f"Research context for: {analysis}",
            "Break work into implementation tasks",
            "Define system architecture and interfaces",
        ],
    }


def architect_node(state: GraphState) -> GraphState:
    result = _architect_agent.run(
        {
            "analysis": state.get("analysis", ""),
            "tasks": state.get("tasks", []),
        }
    )
    return {"architecture": result["architecture"]}


def developer_node(state: GraphState) -> GraphState:
    result = _developer_agent.run(
        {"architecture": state.get("architecture", [])}
    )
    return {"code_plan": result["code_plan"]}


def qa_node(state: GraphState) -> GraphState:
    result = _qa_agent.run({"code_plan": state.get("code_plan", [])})
    return {"tests": result["tests"]}


def finalize_node(state: GraphState) -> GraphState:
    return {
        "final_output": {
            "agent": "planner",
            "analysis": state.get("analysis", ""),
            "tasks": state.get("tasks", []),
            "architecture": state.get("architecture", []),
            "code_plan": state.get("code_plan", []),
            "tests": state.get("tests", []),
            "status": "success",
        },
    }


def _build_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("analyze_node", analyze_node)
    graph.add_node("breakdown_node", breakdown_node)
    graph.add_node("architect_node", architect_node)
    graph.add_node("developer_node", developer_node)
    graph.add_node("qa_node", qa_node)
    graph.add_node("finalize_node", finalize_node)
    graph.add_edge(START, "analyze_node")
    graph.add_edge("analyze_node", "breakdown_node")
    graph.add_edge("breakdown_node", "architect_node")
    graph.add_edge("architect_node", "developer_node")
    graph.add_edge("developer_node", "qa_node")
    graph.add_edge("qa_node", "finalize_node")
    graph.add_edge("finalize_node", END)
    return graph


app_graph = _build_graph().compile()
