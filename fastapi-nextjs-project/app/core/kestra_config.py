import os
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings

class KestraConfig(BaseModel):
    """Configuration for Kestra workflow orchestration."""
    
    # Kestra API settings
    api_url: str = os.getenv("KESTRA_API_URL", "http://localhost:8080")
    
    # Authentication settings
    auth_enabled: bool = os.getenv("KESTRA_AUTH_ENABLED", "").lower() in ("true", "1", "t", "yes")
    username: Optional[str] = os.getenv("KESTRA_USERNAME", None)
    password: Optional[str] = os.getenv("KESTRA_PASSWORD", None)
    api_key: Optional[str] = os.getenv("KESTRA_API_KEY", None)
    
    # Namespace settings
    default_namespace: str = os.getenv("KESTRA_DEFAULT_NAMESPACE", "default")
    
    # Webhook settings
    webhook_url: Optional[str] = os.getenv("KESTRA_WEBHOOK_URL", None)
    webhook_secret: Optional[str] = os.getenv("KESTRA_WEBHOOK_SECRET", None)
    
    # PocketBase integration settings
    pocketbase_url: Optional[str] = os.getenv("POCKETBASE_URL", None)
    pocketbase_email: Optional[str] = os.getenv("POCKETBASE_EMAIL", None)
    pocketbase_password: Optional[str] = os.getenv("POCKETBASE_PASSWORD", None)
    
    # Local settings
    templates_dir: str = os.getenv("KESTRA_TEMPLATES_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates/kestra"))
    flows_dir: str = os.getenv("KESTRA_FLOWS_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/kestra/flows"))
    
    @property
    def is_configured(self) -> bool:
        """Check if Kestra API is configured."""
        return bool(self.api_url)
    
    @property
    def is_auth_configured(self) -> bool:
        """Check if authentication is configured."""
        if not self.auth_enabled:
            return True
        return bool((self.username and self.password) or self.api_key)
    
    @property
    def is_pocketbase_configured(self) -> bool:
        """Check if PocketBase integration is configured."""
        return bool(self.pocketbase_url and self.pocketbase_email and self.pocketbase_password)

# Create a global instance of KestraConfig
kestra_config = KestraConfig()
