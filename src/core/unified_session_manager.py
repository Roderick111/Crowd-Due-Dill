"""
Unified Session Manager

Clean session management using LangGraph's checkpointer as single source of truth.
Eliminates dual persistence and provides robust session handling.
"""

import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.utils.logger import logger


class UnifiedSessionManager:
    """
    Unified session manager using LangGraph checkpointer as single source of truth.
    
    Features:
    - No dual persistence - everything through checkpointer
    - Memory settings stored in graph state
    - Session metadata in graph state
    - Built-in conversation history
    """
    
    def __init__(self, checkpointer, graph):
        self.checkpointer = checkpointer
        self.graph = graph
        self.current_thread_id: Optional[str] = None
        
        # Ensure sessions directory exists for the SQLite database
        os.makedirs("data/sessions", exist_ok=True)
    
    def create_session(self) -> Dict[str, Any]:
        """Create a new session with clean state."""
        thread_id = str(uuid.uuid4())
        
        # Initialize state with default memory settings and metadata
        initial_state = {
            "messages": [],
            "memory_settings": {
                "short_term_enabled": True,
                "medium_term_enabled": True
            },
            "session_metadata": {
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
                "domains_used": []
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Initialize the session by updating state
        self.graph.update_state(config, initial_state)
        
        self.current_thread_id = thread_id
        logger.debug(f"Created session: {thread_id[:8]}...")
        
        return {
            "thread_id": thread_id,
            "config": config,
            "state": initial_state
        }
    
    def load_session(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Load an existing session by thread ID."""
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get current state from checkpointer
            state_snapshot = self.graph.get_state(config)
            
            if state_snapshot and state_snapshot.values:
                self.current_thread_id = thread_id
                logger.debug(f"Loaded session: {thread_id[:8]}...")
                
                return {
                    "thread_id": thread_id,
                    "config": config,
                    "state": state_snapshot.values
                }
            else:
                logger.debug(f"Session {thread_id[:8]}... not found")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load session {thread_id[:8]}...: {e}")
            return None
    
    def delete_session(self, thread_id: str) -> bool:
        """Delete a session and all its checkpoints."""
        try:
            # Use checkpointer's delete_thread method with the correct parameter format
            self.checkpointer.delete_thread(thread_id)
            
            if self.current_thread_id == thread_id:
                self.current_thread_id = None
            
            print(f"🗑️ Session {thread_id[:8]}... deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {thread_id[:8]}...: {e}")
            print(f"❌ Session {thread_id[:8]}... not found")
            return False
    
    def update_activity(self, domains_used: List[str] = None) -> bool:
        """Update current session activity and metadata."""
        if not self.current_thread_id:
            return False
        
        config = {"configurable": {"thread_id": self.current_thread_id}}
        
        try:
            # Get current state
            current_state = self.graph.get_state(config)
            if not current_state or not current_state.values:
                return False
            
            # Update metadata
            metadata = current_state.values.get("session_metadata", {})
            metadata["last_activity"] = datetime.now().isoformat()
            metadata["message_count"] = metadata.get("message_count", 0) + 1
            
            if domains_used:
                current_domains = set(metadata.get("domains_used", []))
                current_domains.update(domains_used)
                metadata["domains_used"] = list(current_domains)
            
            # Update state
            self.graph.update_state(config, {"session_metadata": metadata})
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
            return False
    
    def save_memory_settings(self, memory_manager) -> bool:
        """Save memory settings to current session state."""
        if not self.current_thread_id:
            return False
        
        config = {"configurable": {"thread_id": self.current_thread_id}}
        
        try:
            memory_status = memory_manager.get_memory_status()
            memory_settings = {
                "short_term_enabled": memory_status["short_term"],
                "medium_term_enabled": memory_status["medium_term"]
            }
            
            # Update state with new memory settings
            self.graph.update_state(config, {"memory_settings": memory_settings})
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory settings: {e}")
            return False
    
    def restore_memory_settings(self, memory_manager) -> bool:
        """Restore memory settings from current session state."""
        if not self.current_thread_id:
            return False
        
        config = {"configurable": {"thread_id": self.current_thread_id}}
        
        try:
            # Get current state
            current_state = self.graph.get_state(config)
            if not current_state or not current_state.values:
                return False
            
            memory_settings = current_state.values.get("memory_settings", {
                "short_term_enabled": True,
                "medium_term_enabled": True
            })
            
            # Apply settings to memory manager
            if memory_settings.get("short_term_enabled", True):
                memory_manager.enable_short_term(user_triggered=False)
            else:
                memory_manager.disable_short_term(user_triggered=False)
            
            if memory_settings.get("medium_term_enabled", True):
                memory_manager.enable_medium_term(user_triggered=False)
            else:
                memory_manager.disable_medium_term(user_triggered=False)
            
            logger.debug(f"Restored memory: ST:{memory_settings.get('short_term_enabled', True)}, MT:{memory_settings.get('medium_term_enabled', True)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore memory settings: {e}")
            return False
    
    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent sessions using checkpointer."""
        try:
            sessions_dict = {}
            
            # Get all checkpoints (threads) using the correct API
            # Note: checkpointer.list() returns ALL checkpoints, including multiple per thread
            for checkpoint_tuple in self.checkpointer.list(None, limit=limit*10):  # Get more to account for duplicates
                if not checkpoint_tuple.config:
                    continue
                    
                thread_id = checkpoint_tuple.config.get("configurable", {}).get("thread_id")
                if not thread_id:
                    continue
                
                # Extract metadata from the checkpoint tuple
                metadata = checkpoint_tuple.checkpoint.get("channel_values", {}).get("session_metadata", {})
                message_count = len(checkpoint_tuple.checkpoint.get("channel_values", {}).get("messages", []))
                last_activity = metadata.get("last_activity", "unknown")
                
                # Only keep the most recent checkpoint for each thread_id (latest last_activity)
                if thread_id not in sessions_dict:
                    sessions_dict[thread_id] = {
                        "thread_id": thread_id,
                        "title": metadata.get("title"),
                        "created_at": metadata.get("created_at", "unknown"),
                        "last_activity": last_activity,
                        "message_count": message_count,
                        "domains_used": metadata.get("domains_used", []),
                        "archived": metadata.get("archived", False)
                    }
                else:
                    # Keep the checkpoint with the most recent activity
                    existing_activity = sessions_dict[thread_id]["last_activity"]
                    if last_activity != "unknown" and (existing_activity == "unknown" or last_activity > existing_activity):
                        sessions_dict[thread_id] = {
                            "thread_id": thread_id,
                            "title": metadata.get("title"),
                            "created_at": metadata.get("created_at", "unknown"),
                            "last_activity": last_activity,
                            "message_count": message_count,
                            "domains_used": metadata.get("domains_used", []),
                            "archived": metadata.get("archived", False)
                        }
            
            # Convert dict to list, filter out archived sessions, and sort by last activity (newest first)
            sessions = [s for s in sessions_dict.values() if not s.get("archived", False)]
            sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
            return sessions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def find_session_by_partial_id(self, partial_id: str) -> Optional[str]:
        """Find session by partial thread ID."""
        try:
            # List all sessions and find one that starts with partial_id
            for checkpoint_tuple in self.checkpointer.list(None, limit=100):  
                if not checkpoint_tuple.config:
                    continue
                    
                thread_id = checkpoint_tuple.config.get("configurable", {}).get("thread_id")
                if thread_id and thread_id.startswith(partial_id):
                    return thread_id
            return None
            
        except Exception as e:
            logger.error(f"Failed to find session: {e}")
            return None
    
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current session information."""
        if not self.current_thread_id:
            return None
        
        config = {"configurable": {"thread_id": self.current_thread_id}}
        
        try:
            current_state = self.graph.get_state(config)
            if current_state and current_state.values:
                metadata = current_state.values.get("session_metadata", {})
                memory_settings = current_state.values.get("memory_settings", {})
                message_count = len(current_state.values.get("messages", []))
                
                return {
                    "thread_id": self.current_thread_id,
                    "created_at": metadata.get("created_at", "unknown"),
                    "last_activity": metadata.get("last_activity", "unknown"),
                    "message_count": message_count,
                    "domains_used": metadata.get("domains_used", []),
                    "memory_settings": memory_settings
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get current session: {e}")
            return None
    
    def session_exists(self, thread_id: str) -> bool:
        """Check if session exists."""
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            state_snapshot = self.graph.get_state(config)
            return state_snapshot and state_snapshot.values is not None
        except Exception:
            return False
    
    def update_session_title(self, thread_id: str, title: str) -> bool:
        """Update session title."""
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get current state
            current_state = self.graph.get_state(config)
            if not current_state or not current_state.values:
                return False
            
            # Update metadata with new title
            metadata = current_state.values.get("session_metadata", {})
            metadata["title"] = title
            metadata["last_activity"] = datetime.now().isoformat()
            
            # Update state
            self.graph.update_state(config, {"session_metadata": metadata})
            logger.debug(f"Updated session {thread_id[:8]}... title to: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session title: {e}")
            return False
    
    def archive_session(self, thread_id: str) -> bool:
        """Archive a session by marking it as archived."""
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get current state
            current_state = self.graph.get_state(config)
            if not current_state or not current_state.values:
                return False
            
            # Update metadata to mark as archived
            metadata = current_state.values.get("session_metadata", {})
            metadata["archived"] = True
            metadata["archived_at"] = datetime.now().isoformat()
            metadata["last_activity"] = datetime.now().isoformat()
            
            # Update state
            self.graph.update_state(config, {"session_metadata": metadata})
            logger.debug(f"Archived session {thread_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive session: {e}")
            return False

    def unarchive_session(self, thread_id: str) -> bool:
        """Unarchive a session by removing the archived flag."""
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get current state
            current_state = self.graph.get_state(config)
            if not current_state or not current_state.values:
                return False
            
            # Update metadata to remove archived flag
            metadata = current_state.values.get("session_metadata", {})
            metadata["archived"] = False
            metadata["unarchived_at"] = datetime.now().isoformat()
            metadata["last_activity"] = datetime.now().isoformat()
            
            # Update state
            self.graph.update_state(config, {"session_metadata": metadata})
            logger.debug(f"Unarchived session {thread_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unarchive session: {e}")
            return False

    def list_archived_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List archived sessions using checkpointer."""
        try:
            sessions_dict = {}
            
            # Get all checkpoints (threads) using the correct API
            for checkpoint_tuple in self.checkpointer.list(None, limit=limit*10):  # Get more to account for duplicates
                if not checkpoint_tuple.config:
                    continue
                    
                thread_id = checkpoint_tuple.config.get("configurable", {}).get("thread_id")
                if not thread_id:
                    continue
                
                # Extract metadata from the checkpoint tuple
                metadata = checkpoint_tuple.checkpoint.get("channel_values", {}).get("session_metadata", {})
                message_count = len(checkpoint_tuple.checkpoint.get("channel_values", {}).get("messages", []))
                last_activity = metadata.get("last_activity", "unknown")
                
                # Only keep the most recent checkpoint for each thread_id (latest last_activity)
                if thread_id not in sessions_dict:
                    sessions_dict[thread_id] = {
                        "thread_id": thread_id,
                        "title": metadata.get("title"),
                        "created_at": metadata.get("created_at", "unknown"),
                        "last_activity": last_activity,
                        "message_count": message_count,
                        "domains_used": metadata.get("domains_used", []),
                        "archived": metadata.get("archived", False),
                        "archived_at": metadata.get("archived_at", "unknown")
                    }
                else:
                    # Keep the checkpoint with the most recent activity
                    existing_activity = sessions_dict[thread_id]["last_activity"]
                    if last_activity != "unknown" and (existing_activity == "unknown" or last_activity > existing_activity):
                        sessions_dict[thread_id] = {
                            "thread_id": thread_id,
                            "title": metadata.get("title"),
                            "created_at": metadata.get("created_at", "unknown"),
                            "last_activity": last_activity,
                            "message_count": message_count,
                            "domains_used": metadata.get("domains_used", []),
                            "archived": metadata.get("archived", False),
                            "archived_at": metadata.get("archived_at", "unknown")
                        }
            
            # Convert dict to list, filter to only archived sessions, and sort by archived date (newest first)
            archived_sessions = [s for s in sessions_dict.values() if s.get("archived", False)]
            archived_sessions.sort(key=lambda x: x.get("archived_at", ""), reverse=True)
            return archived_sessions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list archived sessions: {e}")
            return [] 