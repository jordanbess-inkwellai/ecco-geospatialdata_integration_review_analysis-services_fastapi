import os
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings

class BoxConfig(BaseModel):
    """Configuration for Box.com API integration."""
    
    # Client credentials
    client_id: str = os.getenv("BOX_CLIENT_ID", "")
    client_secret: str = os.getenv("BOX_CLIENT_SECRET", "")
    
    # Enterprise ID (optional, for enterprise apps)
    enterprise_id: Optional[str] = os.getenv("BOX_ENTERPRISE_ID", None)
    
    # JWT configuration
    private_key_path: Optional[str] = os.getenv("BOX_PRIVATE_KEY_PATH", None)
    private_key_password: Optional[str] = os.getenv("BOX_PRIVATE_KEY_PASSWORD", None)
    
    # OAuth2 configuration
    redirect_uri: str = os.getenv("BOX_REDIRECT_URI", f"{settings.BACKEND_URL}/api/v1/box/oauth2callback")
    
    # App user configuration
    app_user_name: str = os.getenv("BOX_APP_USER_NAME", "MCP Server")
    
    # Cache settings
    cache_dir: str = os.getenv("BOX_CACHE_DIR", os.path.join(settings.UPLOAD_DIR, "box_cache"))
    
    # Metadata template settings
    metadata_template_scope: str = os.getenv("BOX_METADATA_TEMPLATE_SCOPE", "enterprise")
    metadata_template_name: str = os.getenv("BOX_METADATA_TEMPLATE_NAME", "geospatialMetadata")
    
    # Webhook settings
    webhook_signature_key: Optional[str] = os.getenv("BOX_WEBHOOK_SIGNATURE_KEY", None)
    
    @property
    def is_configured(self) -> bool:
        """Check if Box.com API is configured."""
        return bool(self.client_id and self.client_secret)
    
    @property
    def is_jwt_configured(self) -> bool:
        """Check if JWT authentication is configured."""
        return bool(self.private_key_path and os.path.exists(self.private_key_path))
    
    @property
    def is_oauth_configured(self) -> bool:
        """Check if OAuth2 authentication is configured."""
        return bool(self.client_id and self.client_secret and self.redirect_uri)

# Create a global instance of BoxConfig
box_config = BoxConfig()
