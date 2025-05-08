from typing import Dict, List, Any, Optional
import inspect

class ProcessRegistry:
    """Registry for OGC API Processes"""
    
    def __init__(self):
        self.processes = {}
    
    def register_process(self, process_id: str, process_func, description: str, 
                         inputs: Dict[str, Any], outputs: Dict[str, Any],
                         examples: List[Dict[str, Any]] = None):
        """
        Register a new process
        
        Args:
            process_id: Unique identifier for the process
            process_func: Function that implements the process
            description: Description of the process
            inputs: Dictionary of input parameters
            outputs: Dictionary of output parameters
            examples: Optional list of example inputs
        """
        self.processes[process_id] = {
            "id": process_id,
            "title": process_id.replace("_", " ").title(),
            "description": description,
            "inputs": inputs,
            "outputs": outputs,
            "examples": examples or [],
            "func": process_func
        }
    
    def get_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a process by ID
        
        Args:
            process_id: Process ID
            
        Returns:
            Process definition without the function reference
        """
        if process_id not in self.processes:
            return None
        
        # Return a copy without the function reference
        process = self.processes[process_id].copy()
        process.pop("func", None)
        return process
    
    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        Get all registered processes
        
        Returns:
            List of process summaries
        """
        return [
            {
                "id": p["id"],
                "title": p["title"],
                "description": p["description"]
            }
            for p in self.processes.values()
        ]
    
    def get_process_function(self, process_id: str):
        """
        Get the function for a process
        
        Args:
            process_id: Process ID
            
        Returns:
            Process function
        """
        if process_id not in self.processes:
            return None
        return self.processes[process_id]["func"]
