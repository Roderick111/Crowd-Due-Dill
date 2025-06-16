#!/usr/bin/env python3
"""
Clean Logging System for Esoteric Vectors

Provides structured logging with debug mode support.
Only shows important messages by default, detailed logs in debug mode.
"""

import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

class LogLevel(Enum):
    """Log levels for the system"""
    CRITICAL = "critical"
    ERROR = "error" 
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class EsotericLogger:
    """
    Clean logger for the Esoteric Vectors system.
    
    Shows only important messages by default:
    - System ready messages
    - Q&A cache hits
    - RAG system status
    - Commands and errors
    
    Debug mode shows all technical details.
    """
    
    def __init__(self, debug_mode: Optional[bool] = None):
        """
        Initialize logger.
        
        Args:
            debug_mode: Enable debug logging. If None, reads from ESOTERIC_DEBUG env var
        """
        if debug_mode is None:
            debug_mode = os.getenv('ESOTERIC_DEBUG', 'false').lower() in ('true', '1', 'yes')
        
        self.debug_mode = debug_mode
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup Python logging configuration."""
        # Suppress noisy third-party loggers unless in debug mode
        if not self.debug_mode:
            logging.getLogger('httpx').setLevel(logging.WARNING)
            logging.getLogger('chromadb').setLevel(logging.WARNING)
            logging.getLogger('openai').setLevel(logging.WARNING)
            logging.getLogger('src.utils.resilience').setLevel(logging.WARNING)
    
    def system_ready(self, message: str):
        """Log system ready messages (always shown)."""
        print(f"✅ {message}")
    
    def qa_cache_hit(self, similarity: float, query_preview: str):
        """Log Q&A cache hits (always shown)."""
        print(f"⚡ Q&A Cache Hit! Similarity: {similarity:.3f} for: '{query_preview}...'")
    
    def rag_retrieval(self, chunk_count: int, domains: list):
        """Log RAG retrieval results (always shown)."""
        domain_str = f"from domains: {domains}" if domains else "from all domains"
        print(f"📚 Retrieved {chunk_count} chunks {domain_str}")
    
    def command_executed(self, command: str, result: str = ""):
        """Log command execution (always shown)."""
        if result:
            print(f"✅ {command}: {result}")
        else:
            print(f"✅ {command}")
    
    def error(self, message: str):
        """Log errors (always shown)."""
        print(f"❌ {message}")
    
    def warning(self, message: str):
        """Log warnings (always shown)."""
        print(f"⚠️ {message}")
    
    def info(self, message: str):
        """Log info messages (always shown)."""
        print(f"ℹ️ {message}")
    
    def negative_intent(self, query_preview: str):
        """Log negative intent detection (always shown)."""
        print(f"🛡️ Negative intent detected - bypassing Q&A cache, using RAG for: '{query_preview}...'")
    
    def domain_blocked(self, domains: list):
        """Log domain blocking (always shown)."""
        print(f"🚫 No content found in active domains: {domains}")
    
    def debug(self, message: str):
        """Log debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🔧 DEBUG: {message}")
    
    def debug_resilience(self, message: str):
        """Log resilience debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🛡️ RESILIENCE: {message}")
    
    def debug_chromadb(self, message: str):
        """Log ChromaDB debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🗄️ CHROMADB: {message}")
    
    def debug_openai(self, message: str):
        """Log OpenAI debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🤖 OPENAI: {message}")
    
    def debug_optimization(self, message: str):
        """Log optimization debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🔍 OPTIMIZATION: {message}")
    
    def debug_health(self, message: str):
        """Log health check debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🏥 HEALTH: {message}")
    
    # Memory-specific logging methods
    def memory_toggle(self, memory_type: str, enabled: bool):
        """Log memory toggle operations (debug mode only for system messages)."""
        if self.debug_mode:
            status = "enabled" if enabled else "disabled"
            icon = "✅" if enabled else "🔇"
            print(f"{icon} {memory_type.title()} memory {status}")
    
    def memory_toggle_user(self, memory_type: str, enabled: bool):
        """Log memory toggle operations triggered by user commands (always shown)."""
        status = "enabled" if enabled else "disabled"
        icon = "✅" if enabled else "🔇"
        print(f"{icon} {memory_type.title()} memory {status}")
    

    
    def memory_summary_created(self, message_count: int, summary_length: int):
        """Log medium-term summary creation (always shown)."""
        print(f"🧠 Medium-term summary created: {message_count} messages → {summary_length} chars")
    
    def debug_memory_check(self, message_count: int, should_create: bool, reason: str):
        """Log memory check decisions (debug mode only)."""
        if self.debug_mode:
            decision = "CREATE" if should_create else "SKIP"
            print(f"🧠 MEMORY CHECK: {message_count} messages → {decision} ({reason})")
    
    def debug_memory_trimming(self, original_count: int, trimmed_count: int, method: str):
        """Log message retrieval for short-term memory (debug mode only)."""
        if self.debug_mode:
            print(f"🧠 MEMORY TRIM: {original_count} → {trimmed_count} messages ({method})")
    
    def debug_memory_context(self, has_short_term: bool, has_medium_term: bool, context_length: int):
        """Log memory context building (debug mode only)."""
        if self.debug_mode:
            parts = []
            if has_short_term:
                parts.append("short-term")
            if has_medium_term:
                parts.append("medium-term")
            context_parts = ", ".join(parts) if parts else "none"
            print(f"🧠 MEMORY CONTEXT: {context_parts} → {context_length} chars")
    
    def debug_memory_update_start(self, message_count: int, existing_summary: bool):
        """Log start of memory update process (debug mode only)."""
        if self.debug_mode:
            status = "updating" if existing_summary else "creating initial"
            print(f"🧠 MEMORY UPDATE START: {status} summary for {message_count} messages")
    
    def debug_memory_update_complete(self, success: bool, new_length: int, duration: float):
        """Log completion of memory update process (debug mode only)."""
        if self.debug_mode:
            if success:
                print(f"🧠 MEMORY UPDATE COMPLETE: {new_length} chars in {duration:.3f}s")
            else:
                print(f"🧠 MEMORY UPDATE FAILED after {duration:.3f}s")
    
    def debug_memory_filtering(self, total_messages: int, conversation_messages: int):
        """Log conversation message processing for summarization (debug mode only)."""
        if self.debug_mode:
            print(f"🧠 MEMORY PROCESSING: {total_messages} total → {conversation_messages} conversation messages for summary")
    
    def debug_memory_disabled(self, memory_type: str, operation: str):
        """Log when memory operations are skipped due to being disabled (debug mode only)."""
        if self.debug_mode:
            print(f"🧠 MEMORY SKIP: {memory_type} memory disabled, skipping {operation}")
    
    # Authentication-specific logging methods
    def user_registered(self, username: str):
        """Log user registration (always shown)."""
        print(f"👤 User '{username}' registered successfully")
    
    def user_login(self, username: str):
        """Log user login (always shown)."""
        print(f"🔐 User '{username}' logged in")
    
    def user_logout(self, username: str):
        """Log user logout (always shown)."""
        print(f"👋 User '{username}' logged out")
    
    def user_deleted(self, username: str):
        """Log user deletion (always shown)."""
        print(f"🗑️ User '{username}' deleted")
    
    def auth_required(self, operation: str):
        """Log authentication required messages (always shown)."""
        print(f"🔒 Authentication required for: {operation}")
    
    def debug_auth(self, message: str):
        """Log authentication debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🔒 AUTH DEBUG: {message}")

# Global logger instance
logger = EsotericLogger()

def set_debug_mode(enabled: bool):
    """Enable or disable debug mode globally."""
    global logger
    logger.debug_mode = enabled
    logger._setup_logging()
    if enabled:
        logger.debug("Debug mode enabled")
    else:
        print("✅ Debug mode disabled")

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return logger.debug_mode 