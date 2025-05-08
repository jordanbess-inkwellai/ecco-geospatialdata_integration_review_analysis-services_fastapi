from app.services.process_registry import ProcessRegistry

def register_all_processes(registry: ProcessRegistry):
    """
    Register all processes with the registry
    
    Args:
        registry: Process registry
    """
    from .analysis_processes import register_analysis_processes
    from .search_processes import register_search_processes
    
    # Register basic analysis processes
    register_analysis_processes(registry)
    
    # Register search processes
    register_search_processes(registry)
    
    # Register raster processes if available
    try:
        from .raster_processes import register_raster_processes
        register_raster_processes(registry)
    except ImportError:
        # Raster processes not available
        pass
    
    # Register network processes if pgRouting is available
    try:
        from .network_processes import register_network_processes
        register_network_processes(registry)
    except ImportError:
        # pgRouting processes not available
        pass
