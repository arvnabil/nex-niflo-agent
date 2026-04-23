from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AgentState(BaseModel):
    session_id: str
    user_input: str
    steps: List[Dict[str, Any]] = []
    current_thought: Optional[str] = None
    skill_results: Dict[str, Any] = {}
    is_complete: bool = False
    final_response: Optional[str] = None

    def append_step(self, step_num, key, thought, action, args, observation):
        self.steps.append({
            "step": step_num,
            "key": key,
            "thought": thought,
            "action": action,
            "args": args,
            "observation": observation
        })


class TaskStateStore:
    def __init__(self):
        self._states: Dict[str, AgentState] = {}

    def get_or_create(self, session_id: str, user_input: str) -> AgentState:
        if session_id not in self._states:
            self._states[session_id] = AgentState(session_id=session_id, user_input=user_input)
        return self._states[session_id]

    def clear(self, session_id: str):
        if session_id in self._states:
            del self._states[session_id]

# Singleton
task_state = TaskStateStore()
