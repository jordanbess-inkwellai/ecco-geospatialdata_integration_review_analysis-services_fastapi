from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.process_registry import ProcessRegistry
from app.services.process_executor import ProcessExecutor

class OGCProcessesService:
    """Service for managing OGC API Processes"""
    
    def __init__(self):
        """Initialize the OGC Processes service"""
        self.registry = ProcessRegistry()
        self.executor = ProcessExecutor(self.registry)
        
        # Register processes
        self._register_processes()
    
    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        Get all registered processes
        
        Returns:
            List of process summaries
        """
        return self.registry.get_all_processes()
    
    def get_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a process by ID
        
        Args:
            process_id: Process ID
            
        Returns:
            Process definition
        """
        return self.registry.get_process(process_id)
    
    async def execute_process(self, process_id: str, inputs: Dict[str, Any], db: AsyncSession) -> Any:
        """
        Execute a process with the given inputs
        
        Args:
            process_id: Process ID
            inputs: Process inputs
            db: Database session
            
        Returns:
            Process result
        """
        return await self.executor.execute(process_id, inputs, db)
    
    def _register_processes(self):
        """Register all processes"""
        # Import process registration functions
        from app.services.processes import register_all_processes
        
        # Register all processes
        register_all_processes(self.registry)
