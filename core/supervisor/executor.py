import asyncio
import logging
from core.loop import agent_loop

logger = logging.getLogger("nex-executor")

class DAGExecutor:
    """
    Hybrid Executor (Parallel + Sequential) for Nex Squad.
    Resolves Directed Acyclic Graphs (DAG) of tasks.
    """
    def __init__(self, max_parallel=3):
        self.max_parallel = max_parallel

    async def execute(self, session_id: str, tasks: list):
        """
        Executes a list of tasks respecting dependencies.
        """
        logger.info(f"[EXECUTOR] Planning execution for {len(tasks)} tasks.")
        
        results = {}
        completed_task_ids = set()
        
        # Simple Loop until all tasks are done
        # In a real enterprise system, this would be a dependency resolution queue
        while len(completed_task_ids) < len(tasks):
            # Identify ready tasks (dependencies met and not yet started)
            ready_tasks = [
                t for t in tasks 
                if t['id'] not in completed_task_ids 
                and all(dep in completed_task_ids for dep in t.get('dependencies', []))
            ]
            
            if not ready_tasks:
                if len(completed_task_ids) < len(tasks):
                    logger.error("[EXECUTOR] Deadlock detected or missing dependencies!")
                    break
                break

            # Limit parallelism
            batch = ready_tasks[:self.max_parallel]
            logger.info(f"[EXECUTOR] Running batch of {len(batch)} parallel tasks.")
            
            # Execute batch
            batch_coros = [
                self.run_task(session_id, t) for t in batch
            ]
            
            batch_results = await asyncio.gather(*batch_coros)
            
            # Record results
            for task, res in zip(batch, batch_results):
                results[task['id']] = res
                completed_task_ids.add(task['id'])
        
        return list(results.values())

    async def run_task(self, session_id: str, task: dict):
        """
        Individual worker call.
        """
        agent_id = task.get('agent', 'sovereign')
        description = task.get('task')
        
        logger.info(f"[EXECUTOR] Delegating to {agent_id}: {description}")
        
        # Call the Agent Loop (configured for this specific agent)
        # Note: We pass the task description as the 'user_input' for that agent
        result = await agent_loop.run(session_id, description, agent_id=agent_id)
        return result

# Singleton
dag_executor = DAGExecutor()
