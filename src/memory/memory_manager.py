"""
Memory Manager

Handles short-term and medium-term memory for conversations.
Extracted from main.py to keep the main file focused on orchestration.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, AIMessage
from utils.logger import logger


class MemoryManager:
    """Manages short-term and medium-term memory for conversations."""
    
    def __init__(self, llm, stats_collector=None):
        self.llm = llm
        self.stats_collector = stats_collector
        # Thread pool for parallel summarization (keeping your original approach)
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="memory_")
        
        # Memory toggle flags - can be changed at runtime
        self.short_term_enabled = True
        self.medium_term_enabled = True
        
        # Centralized short-term memory configuration
        self.short_term_message_count = 20  # Single source of truth for short-term memory size
    
    def enable_short_term(self, user_triggered: bool = True) -> bool:
        """Enable short-term memory."""
        self.short_term_enabled = True
        if user_triggered:
            logger.memory_toggle_user("short-term", True)
        else:
            logger.memory_toggle("short-term", True)
        if self.stats_collector:
            self.stats_collector.record_memory_toggle("short_term", True)
        return True
    
    def disable_short_term(self, user_triggered: bool = True) -> bool:
        """Disable short-term memory."""
        self.short_term_enabled = False
        if user_triggered:
            logger.memory_toggle_user("short-term", False)
        else:
            logger.memory_toggle("short-term", False)
        if self.stats_collector:
            self.stats_collector.record_memory_toggle("short_term", False)
        return True
    
    def enable_medium_term(self, user_triggered: bool = True) -> bool:
        """Enable medium-term memory."""
        self.medium_term_enabled = True
        if user_triggered:
            logger.memory_toggle_user("medium-term", True)
        else:
            logger.memory_toggle("medium-term", True)
        if self.stats_collector:
            self.stats_collector.record_memory_toggle("medium_term", True)
        return True
    
    def disable_medium_term(self, user_triggered: bool = True) -> bool:
        """Disable medium-term memory."""
        self.medium_term_enabled = False
        if user_triggered:
            logger.memory_toggle_user("medium-term", False)
        else:
            logger.memory_toggle("medium-term", False)
        if self.stats_collector:
            self.stats_collector.record_memory_toggle("medium_term", False)
        return True
    
    def get_memory_status(self) -> Dict[str, bool]:
        """Get current memory toggle status."""
        return {
            "short_term": self.short_term_enabled,
            "medium_term": self.medium_term_enabled
        }

    def should_create_summary(self, state: Dict[str, Any]) -> bool:
        """Determine if we should create/update medium-term summary."""
        messages = state.get("messages", [])
        context = state.get("context", {})
        message_count = len(messages)
        
        # Check if we need initial summary creation (start from 1st message for testing)
        if not state.get("medium_term_summary") and message_count >= 1:
            logger.debug_memory_check(message_count, True, "initial summary needed")
            return True
        
        # Check if we need to update existing summary (every 10 messages)
        last_summary_count = context.get("last_summary_message_count", 0)
        current_count = len(messages)
        
        should_update = current_count - last_summary_count >= 15
        reason = f"update needed ({current_count - last_summary_count} messages since last)" if should_update else f"too soon ({current_count - last_summary_count} messages since last)"
        logger.debug_memory_check(message_count, should_update, reason)
        
        return should_update

    async def create_medium_term_summary_async(self, messages: list, existing_summary: str = None) -> str:
        """Create or update medium-term summary including both user and agent messages."""
        try:
            # Include both user and agent messages to track full conversation flow
            if not messages:
                return existing_summary or ""
            
            # Format conversation messages for summarization
            conversation_text = []
            user_message_count = 0
            agent_message_count = 0
            
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    conversation_text.append(f"User: {msg.content}")
                    user_message_count += 1
                elif isinstance(msg, AIMessage):
                    conversation_text.append(f"Assistant: {msg.content}")
                    agent_message_count += 1
            
            logger.debug_memory_filtering(len(messages), user_message_count + agent_message_count)
            
            if not conversation_text:
                return existing_summary or ""
            
            # Build summary prompt
            if existing_summary:
                # For updates, focus on recent conversation (last 5 exchanges)
                recent_conversation = conversation_text[-10:]  # Last 10 messages (5 exchanges)
                prompt = f"""Update the existing medium-term memory summary by integrating new conversation content.

Previous Summary:
{existing_summary}

Recent Conversation:
{chr(10).join(recent_conversation)}

Create an evolved summary that:
1. Integrates new insights from both user and assistant exchanges
        2. Updates user's journey, interests, and current regulatory understanding
        3. Tracks what guidance/information was already provided to avoid repetition
4. Notes recurring themes and patterns in the conversation
5. Maintains essential context while staying concise

Format: Key Insights & User Journey | Information Already Provided | Current Interests & Patterns
Target: 500-800 tokens."""
            else:
                # For initial summary - be more concise for minimal conversations
                prompt = f"""Create a concise medium-term memory summary from this conversation.

Conversation:
{chr(10).join(conversation_text)}

IMPORTANT: If this is just a greeting or minimal interaction, create a brief summary noting:
- Basic interaction type (greeting, question, etc.)
- Any interests or topics mentioned
- Current conversation status

Only include substantial content if it exists. Do NOT explain limitations or create templates.

Format with sections only if there's substantial content:
- Key Insights: (only if meaningful insights exist)
        - Information Provided: (only if regulatory guidance was given)  
- Current Focus: (only if clear interests emerged)

Keep concise - aim for 100-300 words maximum."""

            # Use summarization model for efficiency
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor, 
                lambda: self.llm.invoke([HumanMessage(content=prompt)])
            )
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Summary creation error: {e}")
            return existing_summary or ""

    def _create_summary_sync(self, messages: list, existing_summary: str = None) -> str:
        """Helper method to create summary in a separate thread with its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.create_medium_term_summary_async(messages, existing_summary)
            )
        finally:
            loop.close()

    def update_medium_term_memory(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update medium-term memory if needed - runs after response."""
        # Check if medium-term memory is enabled
        if not self.medium_term_enabled:
            logger.debug_memory_disabled("medium-term", "summary creation")
            return {}
            
        if not self.should_create_summary(state):
            return {}
        
        try:
            messages = state.get("messages", [])
            existing_summary = state.get("medium_term_summary")
            message_count = len(messages)
            
            logger.debug_memory_update_start(message_count, bool(existing_summary))
            start_time = time.time()
            
            # Get messages that need to be summarized (beyond short-term window)
            messages_to_summarize = messages[:-self.short_term_message_count] if len(messages) > self.short_term_message_count else messages
            
            # Create summary - handle both sync and async contexts
            try:
                # Check if we're already in an async context (like FastAPI)
                current_loop = asyncio.get_running_loop()
                # If we're in an async context, we need to run in a thread to avoid conflicts
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._create_summary_sync, messages_to_summarize, existing_summary)
                    new_summary = future.result(timeout=30)
            except RuntimeError:
                # No running loop, we can create our own
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    new_summary = loop.run_until_complete(
                        self.create_medium_term_summary_async(messages_to_summarize, existing_summary)
                    )
                finally:
                    loop.close()
            
            duration = time.time() - start_time
            summary_length = len(new_summary) if new_summary else 0
            
            # Update context tracking
            context = state.get("context", {})
            context["last_summary_message_count"] = len(messages)
            context["last_summary_update"] = "success"
            
            # Log completion and record stats
            logger.debug_memory_update_complete(True, summary_length, duration)
            logger.memory_summary_created(message_count, summary_length)
            
            if self.stats_collector:
                self.stats_collector.record_memory_summary_creation(duration, summary_length)
            
            return {
                "medium_term_summary": new_summary,
                "context": context
            }
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            logger.debug_memory_update_complete(False, 0, duration)
            logger.error(f"Medium-term memory update error: {e}")
            return {}

    def get_short_term_messages(self, state: Dict[str, Any]) -> List:
        """Get short-term messages using simple message count (centralized method)."""
        messages = state.get("messages", [])
        original_count = len(messages)
        
        # If short-term memory is disabled, return empty list
        if not self.short_term_enabled:
            logger.debug_memory_disabled("short-term", "message retrieval")
            return []
        
        # Use centralized message count configuration
        short_term_messages = messages[-self.short_term_message_count:] if len(messages) > self.short_term_message_count else messages
        
        trimmed_count = len(short_term_messages)
        logger.debug_memory_trimming(original_count, trimmed_count, f"last {self.short_term_message_count} messages")
        
        if self.stats_collector:
            self.stats_collector.record_short_term_trim()
        
        return short_term_messages

    def get_conversation_history(self, state: Dict[str, Any], current_message: str) -> List[Dict[str, str]]:
        """
        Build conversation history for LLM, handling memory disabled fallback.
        Returns list of {"role": "user/assistant", "content": "..."} dicts.
        """
        conversation_messages = []
        current_message_added = False
        
        # Try to get short-term messages first
        short_term_messages = self.get_short_term_messages(state)
        
        if short_term_messages:
            # Short-term memory enabled - use short-term messages
            for msg in short_term_messages:
                if isinstance(msg, HumanMessage):
                    conversation_messages.append({"role": "user", "content": msg.content})
                    # Check if this is the current message to avoid duplication
                    if msg.content == current_message:
                        current_message_added = True
                elif isinstance(msg, AIMessage):
                    conversation_messages.append({"role": "assistant", "content": msg.content})
        else:
            # Short-term memory disabled - use fallback logic for continuity
            messages = state.get("messages", [])
            # Include last 6 messages (3 exchanges) to maintain conversation flow
            recent_messages = messages[-6:] if len(messages) > 6 else messages[:-1]  # Exclude current message to avoid duplication
            
            for msg in recent_messages:
                if isinstance(msg, HumanMessage):
                    conversation_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    conversation_messages.append({"role": "assistant", "content": msg.content})
        
        # Ensure current message is always included
        if not current_message_added:
            conversation_messages.append({"role": "user", "content": current_message})
        
        return conversation_messages

    def display_memory_status(self, state: Dict[str, Any]):
        """Display current memory status (for memory command)."""
        # Show medium-term memory status
        medium_term = state.get("medium_term_summary")
        if medium_term:
            print(f"🧠 Medium-term Summary ({len(medium_term)} chars):")
            print(f"{medium_term[:200]}...")
        else:
            print("🧠 Medium-term Memory: Not yet created (need 1+ messages)")
        
        # Show short-term memory status
        messages = state.get("messages", [])
        short_term_count = min(self.short_term_message_count, len(messages))
        print(f"💭 Short-term Memory: {short_term_count} messages")
        print(f"📊 Total Messages: {len(messages)}")

    def build_memory_context(self, state: Dict[str, Any]) -> str:
        """Build memory context from short-term and medium-term memory."""
        context_parts = []
        has_medium_term = False
        has_short_term = False
        
        # Add medium-term summary if available and enabled
        if self.medium_term_enabled:
            medium_term_summary = state.get("medium_term_summary")
            if medium_term_summary:
                context_parts.append(f"## Medium-Term Memory (Earlier Conversation Context)\n{medium_term_summary}")
                has_medium_term = True
        else:
            logger.debug_memory_disabled("medium-term", "context building")
        
        # Add short-term messages using centralized method
        if self.short_term_enabled:
            messages = state.get("messages", [])
            if messages:
                short_term_messages = messages[-self.short_term_message_count:]  # Use centralized config
                short_term_text = "\n".join([
                    f"**{msg.__class__.__name__}:** {msg.content}" 
                    for msg in short_term_messages
                ])
                context_parts.append(f"## Short-Term Memory (Recent Messages)\n{short_term_text}")
                has_short_term = True
        else:
            logger.debug_memory_disabled("short-term", "context building")
        
        final_context = "\n\n".join(context_parts) if context_parts else ""
        context_length = len(final_context)
        
        logger.debug_memory_context(has_short_term, has_medium_term, context_length)
        
        if self.stats_collector:
            self.stats_collector.record_memory_context_build()
        
        return final_context

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        memory_status = "Active" if self.executor._threads else "Idle"
        
        # Add toggle status
        status_parts = [memory_status]
        if not self.short_term_enabled:
            status_parts.append("ST:OFF")
        if not self.medium_term_enabled:
            status_parts.append("MT:OFF")
        
        return {
            "status": " ".join(status_parts),
            "description": "Background summarization",
            "toggles": self.get_memory_status()
        }

    def clear_memories(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Clear all memories from the current session."""
        try:
            # Clear medium-term summary
            state_updates = {
                "medium_term_summary": None,
                "context": {}
            }
            
            # Clear message history (keeping current message if any)
            messages = state.get("messages", [])
            if messages:
                # Keep only the last message (current one)
                state_updates["messages"] = messages[-1:]
            else:
                state_updates["messages"] = []
            
            print("🧠 Memories cleared")
            
            if self.stats_collector:
                self.stats_collector.record_memory_toggle("memory_clear", True)
            
            return state_updates
            
        except Exception as e:
            logger.error(f"Memory clearing error: {e}")
            return {}

    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False) 