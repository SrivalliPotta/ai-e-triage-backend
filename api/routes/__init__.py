from .auth_routes import router as auth_router
from .incident_routes import router as incident_router
from .triage_routes import router as triage_router
from .websocket_routes import router as websocket_router

__all__ = ["auth_router", "incident_router", "triage_router", "websocket_router"]
