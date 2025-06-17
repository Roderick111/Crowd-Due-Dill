#!/usr/bin/env python3
"""
Crowdfunding Due Diligence AI Agent - Web API

FastAPI-based web interface for the crowdfunding regulatory guidance system.
Provides REST endpoints for chat, session management, and premium features.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Import existing system components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import (
    domain_manager,
    handle_command,
    memory_manager,
    qa_cache,
    rag_system,
)

# Import Auth0 components
from src.core import (
    Auth0User,
    OptionalUser,
    RequiredUser,
    get_auth0_status,
    is_auth0_enabled,
    stripe_service,
    user_sync_service,
    auth0_management,
)
from src.utils.logger import logger

# Configure logging for web API
logging.basicConfig(level=logging.INFO)
web_logger = logging.getLogger("crowdfunding_web_api")

# Initialize FastAPI app
app = FastAPI(
    title="Crowdfunding Due Diligence API",
    description="Professional regulatory guidance for crowdfunding compliance",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for web frontend access
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8080",  # Alternative dev port
    "http://localhost:5173",  # Vite dev server
    "https://localhost:8443", # HTTPS dev server (frontend)
    "https://localhost:8001", # HTTPS API server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080", 
    "http://127.0.0.1:5173",
    "https://127.0.0.1:8443", # HTTPS dev server (alternative)
    "https://127.0.0.1:8001", # HTTPS API server (alternative)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files will be mounted after all routes are defined

# ==================== PYDANTIC MODELS ====================

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Chat request from frontend"""
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response to frontend"""
    response: str
    session_id: str
    message_type: Optional[str] = None  # "advisory" or "analytical"
    rag_used: Optional[bool] = None
    cache_hit: Optional[bool] = None
    timestamp: datetime

class SystemStatus(BaseModel):
    """System status information"""
    active_domains: List[str]
    available_domains: List[str]
    total_documents: int
    cache_size: int
    memory_enabled: Dict[str, bool]

class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    last_activity: datetime
    domains: List[str]

class CommandRequest(BaseModel):
    """System command request"""
    command: str
    session_id: Optional[str] = None

class CommandResponse(BaseModel):
    """System command response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    status_code: int
    timestamp: datetime
    path: str
    message: Optional[str] = None

class SuccessResponse(BaseModel):
    """Standard success response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class UpdateTitleRequest(BaseModel):
    """Request model for updating session title"""
    title: str

class SessionHistoryResponse(BaseModel):
    """Session history response model"""
    session_id: str
    messages: List[ChatMessage]

class UserSessionsResponse(BaseModel):
    """User sessions response model"""
    sessions: List[Dict[str, Any]]
    user_id: str
    timestamp: datetime

class DomainStatusResponse(BaseModel):
    """Domain status response model"""
    active_domains: List[str]
    available_domains: List[str]

class DomainToggleResponse(BaseModel):
    """Domain toggle response model"""
    success: bool
    message: str
    domain: str
    enabled: bool



class AuthStatusResponse(BaseModel):
    """Authentication status response model"""
    auth0_enabled: bool
    status: str
    timestamp: datetime

class UserInfoResponse(BaseModel):
    """User information response model"""
    user: Dict[str, Any]
    timestamp: datetime

class CreateCheckoutRequest(BaseModel):
    """Request for creating Stripe checkout session"""
    plan_type: str  # "monthly" or "lifetime"

class StripeConfigResponse(BaseModel):
    """Stripe configuration response model"""
    publishable_key: Optional[str]
    enabled: bool

class CheckoutSessionResponse(BaseModel):
    """Checkout session response model"""
    success: bool
    checkout_url: str
    session_id: str
    customer_id: Optional[str] = None

class SubscriptionsResponse(BaseModel):
    """User subscriptions response model"""
    success: bool
    subscriptions: List[Dict[str, Any]]
    user_id: str

class WebhookResponse(BaseModel):
    """Webhook response model"""
    received: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class UserPreferencesRequest(BaseModel):
    """Request model for updating user preferences"""
    memory_preferences: Optional[Dict[str, Any]] = None
    active_domains: Optional[List[str]] = None
    session_settings: Optional[Dict[str, Any]] = None

class VerifySessionResponse(BaseModel):
    """Verify session response model"""
    success: bool
    session_id: Optional[str] = None
    payment_status: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CancelSubscriptionRequest(BaseModel):
    """Cancel subscription request model"""
    subscription_id: str

# ==================== UTILITY FUNCTIONS ====================

def get_graph_and_session_manager():
    """Get the initialized graph and session_manager from main module."""
    from src.main import graph, session_manager
    return graph, session_manager

def get_or_create_session(session_id: Optional[str] = None, user: Optional[Auth0User] = None) -> tuple[str, Dict[str, Any]]:
    """Get existing session or create new one using UnifiedSessionManager with user migration support"""
    _, session_manager = get_graph_and_session_manager()
    
    if session_id:
        # Try to load existing session
        session_info = session_manager.load_session(session_id)
        if session_info:
            session_manager.current_thread_id = session_id
            return session_id, {
                "state": session_info["state"],
                "config": session_info["config"],
                "created_at": session_info["state"].get("session_metadata", {}).get("created_at"),
                "last_activity": session_info["state"].get("session_metadata", {}).get("last_activity"),
                "message_count": len(session_info["state"].get("messages", []))
            }
        else:
            # Session ID provided but not found
            # If user is authenticated and session_id has user prefix, try to find original session
            if user and session_id.startswith(f"user_{user.sub.replace('|', '_')}_"):
                # Extract original session ID
                user_prefix = f"user_{user.sub.replace('|', '_')}_"
                original_session_id = session_id[len(user_prefix):]
                
                # Try to load original session
                original_session_info = session_manager.load_session(original_session_id)
                if original_session_info:
                    # Check if this session has already been migrated to prevent repeated migrations
                    original_metadata = original_session_info["state"].get("session_metadata", {})
                    if original_metadata.get("migrated_to"):
                        web_logger.info(f"⚠️ Session {original_session_id} already migrated to {original_metadata.get('migrated_to')}")
                        raise HTTPException(status_code=404, detail=f"Session {session_id} not found (original session already migrated)")
                    web_logger.info(f"🔄 Migrating session {original_session_id} to user-specific {session_id}")
                    
                    # Create new user-specific session with the same state
                    config = {"configurable": {"thread_id": session_id}}
                    graph, _ = get_graph_and_session_manager()
                    graph.update_state(config, original_session_info["state"])
                    
                    # CRITICAL: Ensure the migrated session is properly persisted
                    session_manager.current_thread_id = session_id
                    
                    # Force a checkpoint save by updating the state again with metadata
                    updated_metadata = original_session_info["state"].get("session_metadata", {})
                    updated_metadata["migrated_from"] = original_session_id
                    updated_metadata["migrated_at"] = datetime.now().isoformat()
                    updated_metadata["last_activity"] = datetime.now().isoformat()
                    
                    # Update the state with migration metadata to ensure persistence
                    graph.update_state(config, {"session_metadata": updated_metadata})
                    
                    # Mark original session as migrated and archive it
                    try:
                        # Update original session to mark it as migrated
                        original_config = {"configurable": {"thread_id": original_session_id}}
                        original_updated_metadata = original_metadata.copy()
                        original_updated_metadata["migrated_to"] = session_id
                        original_updated_metadata["migrated_at"] = datetime.now().isoformat()
                        graph.update_state(original_config, {"session_metadata": original_updated_metadata})
                        
                        # Archive the original session
                        session_manager.archive_session(original_session_id)
                        web_logger.info(f"✅ Original session {original_session_id} marked as migrated and archived")
                    except Exception as e:
                        web_logger.warning(f"Could not mark original session {original_session_id} as migrated: {e}")
                    
                    return session_id, {
                        "state": {**original_session_info["state"], "session_metadata": updated_metadata},
                        "config": config,
                        "created_at": updated_metadata.get("created_at"),
                        "last_activity": updated_metadata.get("last_activity"),
                        "message_count": len(original_session_info["state"].get("messages", []))
                    }
            
            # Session not found and no migration possible
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Create new session only when explicitly requested (first message)
    session_info = session_manager.create_session()
    new_session_id = session_info["thread_id"]
    
    return new_session_id, {
        "state": session_info["state"],
        "config": session_info["config"],
        "created_at": session_info["state"].get("session_metadata", {}).get("created_at"),
        "last_activity": session_info["state"].get("session_metadata", {}).get("last_activity"),
        "message_count": len(session_info["state"].get("messages", []))
    }

def update_session_activity(session_id: str):
    """Update session last activity timestamp using UnifiedSessionManager"""
    _, session_manager = get_graph_and_session_manager()
    session_manager.current_thread_id = session_id
    active_domains = rag_system.get_domain_status().get("active_domains", [])
    session_manager.update_activity(active_domains)

# Root route is now handled by the catch-all static file handler at the end

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint"""
    return {"message": "⚖️"}

@app.get("/apple-touch-icon.png")
async def apple_touch_icon():
    """Apple touch icon endpoint"""
    return {"message": "⚖️", "type": "apple-touch-icon"}

@app.get("/apple-touch-icon-precomposed.png")
async def apple_touch_icon_precomposed():
    """Apple touch icon precomposed endpoint"""
    return {"message": "⚖️", "type": "apple-touch-icon-precomposed"}

@app.get("/robots.txt")
async def robots_txt():
    """Robots.txt endpoint"""
    return JSONResponse(
        content="User-agent: *\nDisallow: /\n",
        media_type="text/plain"
    )

@app.get("/manifest.json")
async def manifest_json():
    """Web app manifest for PWA"""
    return {
        "name": "Crowdfunding Due Diligence",
        "short_name": "CrowdfundingDD",
        "description": "Professional regulatory guidance for crowdfunding compliance",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#000000",
        "icons": [
            {
                "src": "/favicon.ico",
                "sizes": "any",
                "type": "image/x-icon"
            }
        ]
    }

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Crowdfunding Due Diligence API",
        "version": "2.0.0",
        "status": "active",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/chat")
async def chat_info():
    """Information about chat endpoint usage"""
    return {
        "message": "Chat endpoint requires POST method",
        "usage": "POST /chat with JSON body: {'message': 'your message', 'session_id': 'optional'}",
        "example": "curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello!\"}'",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test basic system components
        domain_status = rag_system.get_domain_status()
        auth0_status = get_auth0_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "rag_system": "operational",
                "domain_manager": "operational", 
                "session_manager": "operational",
                "auth0": auth0_status,
                "active_domains": domain_status.get("active_domains", [])
            }
        }
    except Exception as e:
        web_logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest, user: OptionalUser = None):
    """Main chat endpoint - POST only (supports optional authentication)"""
    try:
        # Handle user-specific session management
        if user:
            # Authenticated user - use user-specific session path
            base_session_id = request.session_id
            if base_session_id:
                # Check if session ID is already prefixed to prevent double-prefixing
                user_prefix = f"user_{user.sub.replace('|', '_')}_"
                if base_session_id.startswith(user_prefix):
                    # Already prefixed, use as-is
                    session_id = base_session_id
                else:
                    # Not prefixed, add prefix for isolation
                    session_id = f"{user_prefix}{base_session_id}"
            else:
                session_id = None
        else:
            # Anonymous user - use regular session management
            session_id = request.session_id
        
        # Get or create session (with user migration support)
        session_id, session_data = get_or_create_session(session_id, user)
        current_state = session_data["state"]
        current_config = session_data["config"]
        
        # Sync user data if authenticated
        if user:
            await user_sync_service.sync_user(user)
        
        web_logger.debug(f"Processing message for session {session_id[:8]}...")
        
        # Add user message to state
        current_state["messages"].append(HumanMessage(content=request.message))
        
        # Process through agent graph
        graph, _ = get_graph_and_session_manager()
        result = graph.invoke(current_state, config=current_config)
        
        # Update state with result
        current_state.update(result)
        
        # Update session activity
        update_session_activity(session_id)
        active_domains = rag_system.get_domain_status().get("active_domains", [])
        _, session_manager = get_graph_and_session_manager()
        session_manager.update_activity(active_domains)
        
        # Extract response information
        if current_state.get("messages") and len(current_state["messages"]) > 0:
            last_message = current_state["messages"][-1]
            
            # Determine response type and metadata
            message_type = current_state.get("message_type")
            rag_context = current_state.get("rag_context")
            cache_hit = rag_context == "qa_cache_hit"
            rag_used = bool(rag_context and rag_context != "no_rag")
            
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            return ChatResponse(
                response=response_content,
                session_id=session_id,
                message_type=message_type,
                rag_used=rag_used,
                cache_hit=cache_hit,
                timestamp=datetime.now()
            )
        else:
            raise HTTPException(status_code=500, detail="No response generated")
            
    except Exception as e:
        web_logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status"""
    try:
        # Get system status (domains, documents, cache)
        system_status = {
            "active_domains": list(rag_system.get_domain_status().get("active_domains", [])),
            "available_domains": list(rag_system.get_domain_status().get("available_domains", [])),
            "total_documents": rag_system.get_domain_status().get("total_documents", 0)
        }
        
        # Get memory settings
        memory_settings = memory_manager.get_memory_status()
        
        return SystemStatus(
            active_domains=system_status["active_domains"],
            available_domains=system_status["available_domains"],
            total_documents=system_status["total_documents"],
            cache_size=qa_cache.get_cache_stats()["total_pairs"],
            memory_enabled=memory_settings
        )
    except Exception as e:
        web_logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving system status")

@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions using UnifiedSessionManager"""
    try:
        _, session_manager = get_graph_and_session_manager()
        sessions_list = session_manager.list_sessions(limit=20)
        
        sessions = []
        for session in sessions_list:
            # Parse datetime strings or use current time as fallback
            try:
                created_at = datetime.fromisoformat(session["created_at"]) if session["created_at"] != "unknown" else datetime.now()
                last_activity = datetime.fromisoformat(session["last_activity"]) if session["last_activity"] != "unknown" else datetime.now()
            except:
                created_at = datetime.now()
                last_activity = datetime.now()
            
            sessions.append(SessionInfo(
                session_id=session["thread_id"],
                title=session.get("title"),
                message_count=session["message_count"],
                created_at=created_at,
                last_activity=last_activity,
                domains=session.get("domains_used", [])
            ))
        return sessions
    except Exception as e:
        web_logger.error(f"Session listing error: {e}")
        raise HTTPException(status_code=500, detail="Error listing sessions")

@app.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """Get chat history for a specific session using UnifiedSessionManager"""
    try:
        _, session_manager = get_graph_and_session_manager()
        session_info = session_manager.load_session(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = session_info["state"].get("messages", [])
        
        # Convert messages to API format
        history = []
        for msg in messages:
            if hasattr(msg, 'content'):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                history.append(ChatMessage(
                    role=role,
                    content=msg.content,
                    timestamp=datetime.now()  # Note: we don't store timestamps in current system
                ))
        
        return SessionHistoryResponse(session_id=session_id, messages=history)
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session history")

@app.put("/sessions/{session_id}/title", response_model=SuccessResponse)
async def update_session_title(session_id: str, request: UpdateTitleRequest):
    """Update session title"""
    try:
        title = request.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        _, session_manager = get_graph_and_session_manager()
        
        # Update session title in the database
        success = session_manager.update_session_title(session_id, title)
        
        if success:
            return SuccessResponse(success=True, message="Session title updated")
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session title update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating session title")

@app.post("/sessions/{session_id}/archive", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def archive_session(session_id: str):
    """Archive a session"""
    try:
        _, session_manager = get_graph_and_session_manager()
        
        # Archive session in the database
        success = session_manager.archive_session(session_id)
        
        if success:
            return SuccessResponse(success=True, message="Session archived")
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session archive error: {e}")
        raise HTTPException(status_code=500, detail="Error archiving session")

@app.get("/sessions/archived", response_model=List[SessionInfo])
async def list_archived_sessions():
    """List all archived sessions"""
    try:
        _, session_manager = get_graph_and_session_manager()
        sessions_list = session_manager.list_archived_sessions(limit=50)
        
        sessions = []
        for session in sessions_list:
            # Parse datetime strings or use current time as fallback
            try:
                created_at = datetime.fromisoformat(session["created_at"]) if session["created_at"] != "unknown" else datetime.now()
                last_activity = datetime.fromisoformat(session["last_activity"]) if session["last_activity"] != "unknown" else datetime.now()
            except:
                created_at = datetime.now()
                last_activity = datetime.now()
            
            sessions.append(SessionInfo(
                session_id=session["thread_id"],
                title=session.get("title"),
                message_count=session["message_count"],
                created_at=created_at,
                last_activity=last_activity,
                domains=session.get("domains_used", [])
            ))
        return sessions
    except Exception as e:
        web_logger.error(f"Archived sessions listing error: {e}")
        raise HTTPException(status_code=500, detail="Error listing archived sessions")

@app.post("/sessions/{session_id}/unarchive", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def unarchive_session(session_id: str):
    """Unarchive a session (restore to main list)"""
    try:
        _, session_manager = get_graph_and_session_manager()
        
        # Unarchive session in the database
        success = session_manager.unarchive_session(session_id)
        
        if success:
            return SuccessResponse(success=True, message="Session restored")
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session unarchive error: {e}")
        raise HTTPException(status_code=500, detail="Error restoring session")

@app.delete("/sessions/{session_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def delete_session(session_id: str):
    """Delete a session permanently"""
    try:
        _, session_manager = get_graph_and_session_manager()
        
        # Delete session from the database
        success = session_manager.delete_session(session_id)
        
        if success:
            return SuccessResponse(success=True, message="Session deleted")
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session deletion error: {e}")
        raise HTTPException(status_code=500, detail="Error deleting session")

@app.post("/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute system commands"""
    try:
        session_id, session_data = get_or_create_session(request.session_id)
        current_state = session_data["state"]
        
        # Handle command using existing command handler
        result = handle_command(request.command, current_state)
        
        if result == "restart_session":
            # Handle session restart - new session is already created by UnifiedSessionManager
            new_session_info = current_state.get("_new_session")
            if new_session_info:
                new_session_id = new_session_info["thread_id"]
                return CommandResponse(
                    success=True,
                    message="Session changed",
                    data={"new_session_id": new_session_id}
                )
        elif result:
            return CommandResponse(
                success=True,
                message="Command executed successfully"
            )
        else:
            return CommandResponse(
                success=False,
                message="Unknown command or command failed"
            )
            
    except Exception as e:
        web_logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")

@app.get("/domains", response_model=DomainStatusResponse)
async def get_domains():
    """Get available and active domains"""
    try:
        domain_status = rag_system.get_domain_status()
        return DomainStatusResponse(
            active_domains=domain_status.get("active_domains", []),
            available_domains=domain_status.get("available_domains", [])
        )
    except Exception as e:
        web_logger.error(f"Domain retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving domains")

@app.post("/domains/{domain_name}/toggle", response_model=DomainToggleResponse)
async def toggle_domain(domain_name: str, enable: bool = True):
    """Enable or disable a knowledge domain"""
    try:
        if enable:
            result = domain_manager.enable_domain(domain_name)
        else:
            result = domain_manager.disable_domain(domain_name)
        
        if result:
            action = "enabled" if enable else "disabled"
            return DomainToggleResponse(
                success=True,
                message=f"Domain '{domain_name}' {action}",
                domain=domain_name,
                enabled=enable
            )
        else:
            return DomainToggleResponse(
                success=False,
                message=f"Failed to modify domain '{domain_name}'",
                domain=domain_name,
                enabled=not enable
            )
            
    except Exception as e:
        web_logger.error(f"Domain toggle error: {e}")
        raise HTTPException(status_code=500, detail=f"Error toggling domain: {str(e)}")

# Removed lunar endpoint - not relevant for crowdfunding due diligence

# ==================== AUTH0 ENDPOINTS ====================

@app.get("/auth/status", response_model=AuthStatusResponse)
async def get_auth_status():
    """Get authentication system status"""
    auth0_status = get_auth0_status()
    status_text = "configured" if auth0_status.get("enabled") and auth0_status.get("validator_initialized") else "not_configured"
    
    return AuthStatusResponse(
        auth0_enabled=is_auth0_enabled(),
        status=status_text,
        timestamp=datetime.now()
    )

@app.get("/auth/user", response_model=UserInfoResponse)
async def get_current_user_info(user: RequiredUser):
    """Get current authenticated user information (protected endpoint)"""
    return UserInfoResponse(
        user={
            "id": user.sub,
            "email": user.email,
            "name": user.name,
            "nickname": user.nickname,
            "picture": user.picture,
            "email_verified": user.email_verified,
            "given_name": user.given_name,
            "family_name": user.family_name,
            "memory_preferences": user.memory_preferences,
            "active_domains": user.active_domains,
            "session_settings": user.session_settings,
        },
        timestamp=datetime.now()
    )

@app.get("/auth/debug")
async def debug_auth_token(request: Request):
    """Debug endpoint to check JWT token format and validation"""
    try:
        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {
                "error": "No Authorization header found",
                "headers": dict(request.headers),
                "timestamp": datetime.now().isoformat()
            }
        
        if not auth_header.startswith("Bearer "):
            return {
                "error": "Invalid Authorization header format",
                "auth_header": auth_header[:50] + "..." if len(auth_header) > 50 else auth_header,
                "timestamp": datetime.now().isoformat()
            }
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Check token format
        token_parts = token.split('.')
        is_jwt = len(token_parts) == 3
        
        debug_info = {
            "token_received": True,
            "token_length": len(token),
            "token_format": "JWT" if is_jwt else "Opaque",
            "token_parts": len(token_parts),
            "token_preview": token[:50] + "..." if len(token) > 50 else token,
            "timestamp": datetime.now().isoformat()
        }
        
        if is_jwt:
            try:
                # Try to decode header without verification
                from src.core.auth0_validator import _get_unverified_header
                header = _get_unverified_header(token)
                debug_info["jwt_header"] = header
                debug_info["has_kid"] = "kid" in header
            except Exception as header_error:
                debug_info["header_decode_error"] = str(header_error)
        
        # Try to validate with our validator
        try:
            from src.core.auth0_validator import auth0_validator
            if auth0_validator:
                user = await auth0_validator.validate_token(token)
                debug_info["validation_success"] = True
                debug_info["user_sub"] = user.sub
                debug_info["user_email"] = user.email
            else:
                debug_info["validation_error"] = "Auth0 validator not initialized"
        except Exception as validation_error:
            debug_info["validation_error"] = str(validation_error)
        
        return debug_info
        
    except Exception as e:
        return {
            "error": f"Debug endpoint error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.put("/auth/user/preferences", response_model=SuccessResponse)
async def update_user_preferences(user: RequiredUser, preferences: UserPreferencesRequest):
    """Update user preferences (protected endpoint)"""
    try:
        success = await user_sync_service.update_user_metadata(user, {
            "memory_preferences": preferences.memory_preferences or {},
            "active_domains": preferences.active_domains or [],
            "session_settings": preferences.session_settings or {}
        })
        
        if success:
            return SuccessResponse(
                success=True,
                message="User preferences updated"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
            
    except Exception as e:
        web_logger.error(f"Preference update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating user preferences")

@app.get("/auth/user/sessions", response_model=UserSessionsResponse)
async def get_user_sessions(user: RequiredUser):
    """Get sessions for authenticated user (protected endpoint)"""
    try:
        _, session_manager = get_graph_and_session_manager()
        
        # Filter sessions by user prefix
        user_prefix = f"user_{user.sub.replace('|', '_')}_"
        all_sessions = session_manager.list_sessions(limit=50)
        
        user_sessions = []
        for session in all_sessions:
            if session["thread_id"].startswith(user_prefix):
                # Remove user prefix from session ID for frontend
                display_session_id = session["thread_id"][len(user_prefix):]
                
                try:
                    created_at = datetime.fromisoformat(session["created_at"]) if session["created_at"] != "unknown" else datetime.now()
                    last_activity = datetime.fromisoformat(session["last_activity"]) if session["last_activity"] != "unknown" else datetime.now()
                except:
                    created_at = datetime.now()
                    last_activity = datetime.now()
                
                user_sessions.append({
                    "session_id": display_session_id,
                    "internal_id": session["thread_id"],
                    "title": session.get("title"),
                    "message_count": session["message_count"],
                    "created_at": created_at.isoformat(),
                    "last_activity": last_activity.isoformat(),
                    "domains": session.get("domains_used", [])
                })
        
        return UserSessionsResponse(
            sessions=user_sessions,
            user_id=user.sub,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        web_logger.error(f"User sessions error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user sessions")

# Protected admin endpoints
@app.post("/admin/command", response_model=CommandResponse)
async def execute_admin_command(request: CommandRequest, user: RequiredUser):
    """Execute system command (protected endpoint - requires authentication)"""
    try:
        web_logger.debug(f"Admin command from user {user.sub}: {request.command}")
        
        # Execute command using existing command handler
        result = handle_command(request.command)
        
        return CommandResponse(
            success=True,
            message=f"Command executed by {user.name or user.nickname}",
            data={"result": result, "user": user.sub}
        )
    except Exception as e:
        web_logger.error(f"Admin command error: {e}")
        return CommandResponse(
            success=False,
            message=f"Command execution failed: {str(e)}",
            data={"user": user.sub}
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper JSON responses"""
    error_response = ErrorResponse(
        error=exc.detail,
        status_code=exc.status_code,
        timestamp=datetime.now(),
        path=str(request.url.path),
        message="HTTP error occurred"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_response.error,
            "status_code": error_response.status_code,
            "timestamp": error_response.timestamp.isoformat(),
            "path": error_response.path,
            "message": error_response.message
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with proper logging and response"""
    web_logger.error(f"Unhandled error on {request.url.path}: {exc}")
    
    error_response = ErrorResponse(
        error="Internal server error",
        status_code=500,
        timestamp=datetime.now(),
        path=str(request.url.path),
        message="An unexpected error occurred. Please try again later."
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": error_response.error,
            "status_code": error_response.status_code,
            "timestamp": error_response.timestamp.isoformat(),
            "path": error_response.path,
            "message": error_response.message
        }
    )

# ============================================================================
# STRIPE PAYMENT ENDPOINTS
# ============================================================================

@app.get("/stripe/config", response_model=StripeConfigResponse)
async def get_stripe_config():
    """Get Stripe configuration for frontend"""
    config = stripe_service.get_config()
    return StripeConfigResponse(
        publishable_key=config.get("publishable_key"),
        enabled=config.get("enabled", False)
    )

@app.get("/stripe/debug")
async def debug_stripe():
    """Debug endpoint to check Stripe service state during request."""
    # Get the secret key from environment since it's not stored in the service
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    return {
        "enabled": stripe_service.enabled,
        "has_secret_key": bool(secret_key),
        "secret_key_preview": secret_key[:10] + "..." if secret_key else None,
        "has_client": stripe_service.client is not None,
        "client_type": type(stripe_service.client).__name__ if stripe_service.client else None
    }

@app.post("/stripe/create-checkout-session", response_model=CheckoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    user: RequiredUser
):
    """Create Stripe checkout session (requires authentication)"""
    
    # Determine base URL from environment or request headers
    base_url = os.getenv('FRONTEND_URL', 'https://crowdfunding-dd.beautiful-apps.com')
    
    # Fallback to localhost for development
    if not base_url or base_url == 'localhost':
        base_url = "https://localhost:8443"
    
    success_url = f"{base_url}?payment=success&plan={request.plan_type}&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}?payment=canceled"
    
    try:
        # Context7 Best Practice: Stripe Python client is synchronous
        session_data = stripe_service.create_checkout_session(
            plan_type=request.plan_type,
            user_email=user.email or f"{user.sub}@auth0.local",
            user_id=user.sub,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        logger.debug(f"✅ Checkout session created for user {user.sub}: {session_data['session_id']}")
        
        return CheckoutSessionResponse(
            success=True,
            checkout_url=session_data["url"],
            session_id=session_data["session_id"],
            customer_id=session_data.get("customer_id")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from stripe_service
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment session"
        )

@app.get("/stripe/subscriptions", response_model=SubscriptionsResponse)
async def get_user_subscriptions(user: RequiredUser):
    """Get user's Stripe subscriptions"""
    try:
        subscriptions = stripe_service.get_customer_subscriptions(
            user_email=user.email or "user@example.com"
        )
        
        return SubscriptionsResponse(
            success=True,
            subscriptions=[sub.dict() for sub in subscriptions],
            user_id=user.sub
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching user subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription information"
        )

@app.post("/stripe/webhook", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events with enhanced processing"""
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            logger.warning("Webhook received without Stripe signature")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )
        
        # Process webhook (now returns detailed result instead of raising exceptions)
        result = await stripe_service.handle_webhook(payload, signature)
        
        # Log webhook processing result
        if result.get("status") == "processed":
            logger.debug(f"🔔 Webhook processed successfully: {result.get('event_type')}")
        elif result.get("status") == "ignored":
            logger.debug(f"🔔 Webhook ignored: {result.get('reason')}")
        elif result.get("status") == "error":
            logger.error(f"🔔 Webhook processing error: {result.get('reason')}")
        
        # Always return 200 to Stripe (Context7 best practice)
        return WebhookResponse(received=True, result=result)
        
    except Exception as e:
        logger.error(f"❌ Webhook processing failed: {e}")
        # Still return 200 to prevent Stripe retries for non-recoverable errors
        return WebhookResponse(received=True, error=str(e))

@app.get("/auth/premium-status", response_model=Dict[str, Any])
async def get_user_premium_status(user: RequiredUser):
    """Get current user's premium status"""
    try:
        status = await auth0_management.get_user_premium_status(user.sub)
        return {
            "success": True,
            "user_id": user.sub,
            "premium_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        web_logger.error(f"Error getting premium status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get premium status"
        )

@app.get("/admin/premium-users", response_model=Dict[str, Any])
async def list_premium_users(user: RequiredUser):
    """List all premium users (admin only)"""
    try:
        # TODO: Add admin role check here
        premium_users = await auth0_management.list_premium_users()
        return {
            "success": True,
            "premium_users": premium_users,
            "count": len(premium_users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        web_logger.error(f"Error listing premium users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list premium users"
        )

@app.get("/stripe/verify-session/{session_id}", response_model=VerifySessionResponse)
async def verify_checkout_session(session_id: str):
    """Verify a Stripe checkout session for security"""
    try:
        result = stripe_service.verify_session(session_id)
        
        if result.get("success"):
            return VerifySessionResponse(
                success=True,
                session_id=result.get("session_id"),
                payment_status=result.get("payment_status"),
                customer_id=result.get("customer_id"),
                metadata=result.get("metadata", {})
            )
        else:
            return VerifySessionResponse(
                success=False,
                error=result.get("error", "Session verification failed")
            )
            
    except Exception as e:
        logger.error(f"❌ Error verifying session {session_id}: {e}")
        return VerifySessionResponse(
            success=False,
            error="Session verification failed"
        )

@app.post("/stripe/cancel-subscription", response_model=SuccessResponse)
async def cancel_user_subscription(user: RequiredUser, request: CancelSubscriptionRequest):
    """Cancel user's subscription"""
    try:
        success = stripe_service.cancel_subscription(request.subscription_id)
        
        if success:
            return SuccessResponse(
                success=True,
                message="Subscription will be canceled at the end of the current period",
                data={"subscription_id": request.subscription_id}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel subscription"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

# ==================== STATIC FILE MOUNTING ====================
# Mount static files after all routes are defined to avoid conflicts
if os.path.exists("web"):
    # Mount subdirectories first
    for subdir in ["components", "hooks", "services", "config"]:
        subdir_path = f"web/{subdir}"
        if os.path.exists(subdir_path):
            app.mount(f"/{subdir}", StaticFiles(directory=subdir_path), name=f"static_{subdir}")
    
    # Handle root route explicitly
    @app.get("/")
    async def serve_root():
        """Serve the main web interface"""
        return FileResponse("web/index.html")
    
    # Mount root web files (CSS, JS, etc.) but exclude API paths
    # This catch-all mount should be last
    @app.get("/{file_path:path}")
    async def serve_static_files(file_path: str):
        """Serve static files from web directory, but only for non-API paths"""
        # Skip API paths to avoid conflicts
        if file_path.startswith(('api', 'auth', 'chat', 'health', 'status', 'sessions', 'domains', 'stripe', 'admin', 'command', 'favicon.ico', 'apple-touch-icon', 'robots.txt', 'manifest.json')):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve files from web directory
        file_full_path = os.path.join("web", file_path)
        if os.path.exists(file_full_path) and os.path.isfile(file_full_path):
            return FileResponse(file_full_path)
        
        # File not found
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    print("⚖️ Starting Crowdfunding Due Diligence AI Agent Web API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Health Check: http://localhost:8000/health")
    print("💬 Chat Endpoint: POST http://localhost:8000/chat")
    
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )