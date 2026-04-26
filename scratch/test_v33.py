import asyncio
import sys
import os

# Add project root to path
sys.path.append("/home/nabil/projects/nex-niflo-agent")

from core.v2.executor import MissionExecutor
from core.v2.agent import NexAgent
from core.v2.tools import ToolManager

async def test():
    agent = NexAgent("scheduler", "Manajemen Waktu & Penjadwalan Efisien.")
    tools = ToolManager()
    executor = MissionExecutor(agent, tools)
    
    task = "buat meeting"
    state = {"pending_clarification": None}
    
    print(f"--- TESTING INPUT: {task} ---")
    try:
        async for chunk in executor.run_mission_stream(task, history="", state=state):
            print(f"CHUNK: {chunk}")
        print(f"FINAL STATE: {state}")
    except Exception as e:
        print(f"FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
