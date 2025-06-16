#!/usr/bin/env python3
"""
Command Handler for Crowdfunding Due Diligence AI System

Centralized command processing for system management and administration.

Clean command processing with registry pattern:
- Categorized command handlers
- Simple registration system
- Easy to extend and test
"""

import time
import getpass
from typing import Dict, Callable, Any, Union
from utils.logger import logger


class CommandHandler:
    """
    Clean command handler with registry pattern.
    
    Features:
    - Category-based organization
    - Simple command registration
    - Automatic help generation
    - Easy testing and maintenance
    """
    
    def __init__(self):
        """Initialize command registry."""
        self.commands: Dict[str, Callable] = {}
        self.help_text: Dict[str, str] = {}
        
        # Will be injected by main.py
        self.rag_system = None
        self.qa_cache = None
        self.memory_manager = None
        self.session_manager = None
        self.print_stats = None
        self.set_debug_mode = None
    
    def register_dependencies(self, **kwargs):
        """Inject dependencies from main.py."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Register all commands after dependencies are set
        self._register_all_commands()
    
    def register_command(self, command: str, handler: Callable, help_text: str = ""):
        """Register a command with its handler."""
        self.commands[command] = handler
        if help_text:
            self.help_text[command] = help_text
    
    def handle_command(self, user_input: str, state: dict) -> Union[bool, str]:
        """
        Handle user command if it exists.
        
        Args:
            user_input: User's input string
            state: Current conversation state
            
        Returns:
            True if command was handled, False if not recognized
            "restart_session" if session change is requested
        """
        # Handle session commands
        if user_input.startswith("session "):
            return self._handle_session_commands(user_input, state)
        
        # Handle prefix commands (like "domains enable/disable")
        handled = self._handle_prefix_commands(user_input, state)
        if handled:
            return True
        
        # Handle exact match commands
        if user_input in self.commands:
            try:
                self.commands[user_input](state)
                return True
            except Exception as e:
                logger.error(f"Command '{user_input}' failed: {e}")
                return True
        
        return False
    
    def _handle_prefix_commands(self, user_input: str, state: dict) -> bool:
        """Handle commands that start with specific prefixes."""
        # Domain commands
        if user_input.startswith("domains enable "):
            domain = user_input.replace("domains enable ", "").strip()
            return self._handle_domain_enable(domain)
        elif user_input.startswith("domains disable "):
            domain = user_input.replace("domains disable ", "").strip()
            return self._handle_domain_disable(domain)
        
        # Memory commands
        elif user_input.startswith("memory enable "):
            memory_type = user_input.replace("memory enable ", "").strip()
            return self._handle_memory_enable(memory_type, state)
        elif user_input.startswith("memory disable "):
            memory_type = user_input.replace("memory disable ", "").strip()
            return self._handle_memory_disable(memory_type, state)
        
        return False
    
    def _handle_session_commands(self, command: str, state: Dict[str, Any]) -> Union[bool, str]:
        """
        Handle session commands.
        
        Returns:
        - True: Command handled successfully
        - "restart_session": Signal to restart with new session
        """
        
        if command == "session list":
            return self._handle_session_list()
        
        elif command == "session info":
            return self._handle_session_info(state)
        
        elif command.startswith("session change "):
            return self._handle_session_change(command, state)
        
        elif command.startswith("session delete "):
            return self._handle_session_delete(command, state)
        
        return False
    
    def _register_all_commands(self):
        """Register all available commands."""
        # Stats & System Commands
        self.register_command("stats", self._cmd_stats, "Show system statistics")
        
        # Memory Commands
        self.register_command("memory", self._cmd_memory_status, "Show memory status")
        self.register_command("memory status", self._cmd_memory_status, "Show memory status")
        self.register_command("memory clear", self._cmd_memory_clear, "Clear all memories")
        
        # Cache Commands
        self.register_command("cache clear", self._cmd_cache_clear, "Clear RAG caches")
        self.register_command("cache stats clear", self._cmd_cache_stats_clear, "Clear cache statistics")
        self.register_command("qa cache clear", self._cmd_qa_cache_clear, "Clear Q&A cache")
        
        # Domain Commands
        self.register_command("domains", self._cmd_domain_status, "Show domain status")
        

        
        # Debug Commands
        self.register_command("debug on", self._cmd_debug_on, "Enable debug mode")
        self.register_command("debug off", self._cmd_debug_off, "Disable debug mode")
    
    # ===================
    # Command Implementations
    # ===================
    
    def _cmd_stats(self, state: dict):
        """Show system statistics."""
        if self.print_stats:
            self.print_stats()
    
    def _cmd_memory_status(self, state: dict):
        """Show memory status."""
        self.memory_manager.display_memory_status(state)
    
    def _cmd_memory_clear(self, state: dict):
        """Clear all memories from current session."""
        memory_updates = self.memory_manager.clear_memories(state)
        state.update(memory_updates)
        self.session_manager.save_memory_settings(self.memory_manager)
    
    def _cmd_cache_clear(self, state: dict):
        """Clear RAG system caches."""
        self.rag_system.clear_caches()
    
    def _cmd_cache_stats_clear(self, state: dict):
        """Clear cache statistics."""
        self.rag_system.stats_collector.reset_query_stats()
        logger.command_executed("Query statistics cleared")
    
    def _cmd_qa_cache_clear(self, state: dict):
        """Clear Q&A cache."""
        self.qa_cache.clear_cache()
    
    def _cmd_domain_status(self, state: dict):
        """Show domain status."""
        status = self.rag_system.get_domain_status()
        active = ', '.join(status['active_domains']) if status['active_domains'] else 'None'
        print(f"🎯 Active: {active}")
        print(f"Available: {', '.join(status['available_domains'])}")
    

    
    def _cmd_debug_on(self, state: dict):
        """Enable debug mode."""
        if self.set_debug_mode:
            self.set_debug_mode(True)
    
    def _cmd_debug_off(self, state: dict):
        """Disable debug mode."""
        if self.set_debug_mode:
            self.set_debug_mode(False)
    
    # ===================
    # Prefix Command Handlers
    # ===================
    
    def _handle_domain_enable(self, domain: str) -> bool:
        """Enable a specific domain."""
        if self.rag_system.enable_domain(domain):
            logger.command_executed(f"Domain '{domain}' enabled")
        else:
            logger.error(f"Failed to enable domain '{domain}'")
        return True
    
    def _handle_domain_disable(self, domain: str) -> bool:
        """Disable a specific domain."""
        if self.rag_system.disable_domain(domain):
            logger.command_executed(f"Domain '{domain}' disabled")
        else:
            logger.error(f"Failed to disable domain '{domain}'")
        return True
    
    def _handle_memory_enable(self, memory_type: str, state: dict) -> bool:
        """Enable memory type (short/medium)."""
        if memory_type == "short":
            self.memory_manager.enable_short_term()
            self.session_manager.save_memory_settings(self.memory_manager)
        elif memory_type == "medium":
            self.memory_manager.enable_medium_term()
            self.session_manager.save_memory_settings(self.memory_manager)
        else:
            logger.error(f"Unknown memory type: {memory_type}")
            return False
        return True
    
    def _handle_memory_disable(self, memory_type: str, state: dict) -> bool:
        """Disable memory type (short/medium)."""
        if memory_type == "short":
            self.memory_manager.disable_short_term()
            self.session_manager.save_memory_settings(self.memory_manager)
        elif memory_type == "medium":
            self.memory_manager.disable_medium_term()
            self.session_manager.save_memory_settings(self.memory_manager)
        else:
            logger.error(f"Unknown memory type: {memory_type}")
            return False
        return True
    
    # ===================
    # Session Command Handlers
    # ===================
    
    def _handle_session_list(self) -> bool:
        """Handle 'session list' command."""
        sessions = self.session_manager.list_sessions(limit=5)
        if sessions:
            print("📋 Recent sessions:")
            for i, session in enumerate(sessions):
                session_id = session["thread_id"][:8]
                created = session["created_at"][:19].replace('T', ' ')
                msg_count = session["message_count"]
                domains = ', '.join(session["domains_used"]) or 'None'
                print(f"  {i+1}. {session_id}... ({created}) - {msg_count} msgs, domains: {domains}")
        else:
            print("📋 No sessions found")
        return True
    
    def _handle_session_info(self, state: Dict[str, Any]) -> bool:
        """Handle 'session info' command."""
        current_session = self.session_manager.get_current_session()
        if current_session:
            memory_settings = current_session["memory_settings"]
            print(f"🆔 Current Session: {current_session['thread_id'][:8]}...")
            print(f"📅 Created: {current_session['created_at'][:19].replace('T', ' ')}")
            print(f"💬 Messages: {current_session['message_count']}")
            print(f"🎯 Domains used: {', '.join(current_session['domains_used']) or 'None'}")
            print(f"🧠 Memory: ST:{memory_settings.get('short_term_enabled', True)}, MT:{memory_settings.get('medium_term_enabled', True)}")
        else:
            print("🆔 No active session")
        return True
    
    def _handle_session_change(self, command: str, state: Dict[str, Any]) -> Union[bool, str]:
        """Handle 'session change <id|new>' command."""
        session_input = command.replace("session change ", "").strip()
        
        if session_input == "new":
            # Create new session and signal restart
            new_session_info = self.session_manager.create_session()
            state["_new_session"] = new_session_info
            return "restart_session"
        
        else:
            # Try to find and switch to existing session
            full_session_id = self.session_manager.find_session_by_partial_id(session_input)
            if full_session_id:
                session_info = self.session_manager.load_session(full_session_id)
                if session_info:
                    state["_new_session"] = session_info
                    return "restart_session"
                else:
                    print(f"❌ Failed to load session {session_input}")
                    return True
            else:
                print(f"❌ Session not found: {session_input}")
                print("💡 Use 'session list' to see available sessions")
                return True
    
    def _handle_session_delete(self, command: str, state: Dict[str, Any]) -> bool:
        """Handle 'session delete <id>' command."""
        session_input = command.replace("session delete ", "").strip()
        
        # Find session by partial ID
        full_session_id = self.session_manager.find_session_by_partial_id(session_input)
        if not full_session_id:
            print(f"❌ Session not found: {session_input}")
            print("💡 Use 'session list' to see available sessions")
            return True
        
        # Check if trying to delete current session
        current_session = self.session_manager.get_current_session()
        if current_session and full_session_id == current_session["thread_id"]:
            print(f"❌ Cannot delete current active session {session_input}")
            print("💡 Switch to another session first, then delete this one")
            return True
        
        # Delete the session
        success = self.session_manager.delete_session(full_session_id)
        if success:
            logger.debug("Session state cleanup completed")
        
        return True
    
    def get_available_commands(self) -> Dict[str, str]:
        """Get all available commands with help text."""
        return self.help_text.copy()


# Global command handler instance
command_handler = CommandHandler() 