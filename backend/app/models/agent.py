from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    agent_name: str
    input: dict


class AgentRunResponse(BaseModel):
    agent: str
    output: dict


class AgentListResponse(BaseModel):
    agents: list[str]
