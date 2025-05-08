from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.process_registry import ProcessRegistry

class ProcessExecutor:
    """Executor for OGC API Processes"""
    
    def __init__(self, registry: ProcessRegistry):
        """
        Initialize the process executor
        
        Args:
            registry: Process registry
        """
        self.registry = registry
    
    async def execute(self, process_id: str, inputs: Dict[str, Any], db: AsyncSession) -> Any:
        """
        Execute a process with the given inputs
        
        Args:
            process_id: Process ID
            inputs: Process inputs
            db: Database session
            
        Returns:
            Process result
            
        Raises:
            ValueError: If the process is not found
        """
        process_func = self.registry.get_process_function(process_id)
        if not process_func:
            raise ValueError(f"Process {process_id} not found")
        
        # Execute the process function
        result = await process_func(inputs, db)
        return result
