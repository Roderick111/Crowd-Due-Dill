#!/usr/bin/env python3
"""
Crowdfunding Due Diligence AI Agent - Main Application

Clean multi-agent system with:
- Professional advisory and technical analytical response modes
- Domain-aware RAG retrieval
- Q&A cache optimization
- Memory management
- Session persistence
"""

from dotenv import load_dotenv
from typing import Annotated, Literal, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
import sys
from pathlib import Path

# Add src directory to Python path for proper relative imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.contextual_rag import OptimizedContextualRAGSystem
from core.resilience_manager import resilience_manager
from core.stats_collector import StatsCollector
from core.unified_session_manager import UnifiedSessionManager
from cache.negative_intent_detector import NegativeIntentDetector
from cache.qa_cache import QACache
from utils.logger import logger, set_debug_mode
from memory import MemoryManager
from utils.command_handler import command_handler


load_dotenv()

# Initialize LLM
llm = init_chat_model("gemini-1.5-flash-8b", model_provider="google_genai")

# Initialize system components
# Simplified system without domain complexity
negative_detector = NegativeIntentDetector()
qa_cache = QACache()
rag_system = OptimizedContextualRAGSystem()

# Initialize memory manager with stats collector
memory_manager = MemoryManager(llm, rag_system.stats_collector)

# Session manager will be initialized after graph compilation

class CombinedDecision(BaseModel):
    """Combined classification and RAG decision for optimal performance."""
    message_type: Literal["advisory", "analytical"] = Field(
        description="Whether message needs professional advisory support or technical analysis"
    )
    should_use_rag: bool = Field(
        description="True if query involves crowdfunding regulations, legal compliance, or regulatory guidance"
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None
    should_use_rag: bool | None
    rag_context: str | None
    # Medium-term memory fields
    medium_term_summary: str | None
    context: dict[str, Any]  # For tracking summarization state
    # Unified session and memory persistence
    memory_settings: dict[str, Any]  # Memory toggle states
    session_metadata: dict[str, Any]  # Session info (domains, counts, etc.)

def classify_and_decide_rag(state: State):
    """Combined message classification and RAG decision for optimal performance."""
    last_message = state["messages"][-1]
    combined_classifier = llm.with_structured_output(CombinedDecision)

    result = combined_classifier.invoke([
        {
            "role": "system",
            "content": """Classify message type and decide RAG usage:
            
Message types: 
- 'advisory': business concerns, compliance anxiety, need for reassurance about regulatory decisions, strategic guidance requests, risk assessment concerns
- 'analytical': technical questions about regulations, legal definitions, compliance procedures, regulatory analysis, factual information requests, detailed regulatory breakdowns

Use RAG knowledge base if user:
- Asks about crowdfunding regulations (EU, national, or international)
- Needs guidance on compliance requirements and procedures
- Seeks information about legal definitions or regulatory frameworks
- Asks about investment limits, authorization requirements, or investor protection
- Inquires about cross-border crowdfunding services
- Needs clarification on regulatory obligations for platforms or projects
- Asks about enforcement, penalties, or regulatory authorities
- Seeks guidance on specific regulatory articles or provisions

Do NOT use RAG for:
- Simple greetings or general conversation  
- Non-regulatory topics (weather, cooking, general business advice)
- Basic definitions that don't require regulatory context
- Simple factual questions that can be answered with general knowledge"""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    
    return {
        "message_type": result.message_type,
        "should_use_rag": result.should_use_rag
    }



def router(state: State):
    """Route to appropriate agent based on message type."""
    message_type = state.get("message_type", "analytical")
    return {"next": "advisory" if message_type == "advisory" else "analytical"}

def get_rag_context(query: str, should_use_rag: bool) -> dict:
    """Get RAG context for the query."""
    if not should_use_rag:
        return {"type": "no_rag", "content": ""}
    
    try:
        # Use RAG system for retrieval
        rag_result = rag_system.query(query, k=4)
        
        # Check if we got results
        query_type = rag_result.get("metadata", {}).get("query_type", "unknown")
        
        if query_type == "rag" and rag_result.get("chunks"):
            # Build context from chunks
            context_parts = []
            for chunk in rag_result["chunks"]:
                content = chunk.get("content", "")
                if content:
                    context_parts.append(content)
            
            if context_parts:
                context = "\n\n".join(context_parts)
                return {"type": "rag_context", "content": context}
        
        # No relevant content found
        return {"type": "no_rag", "content": ""}
        
    except Exception as e:
        logger.error(f"RAG context error: {e}")
        return {"type": "no_rag", "content": ""}

def create_agent_response(state: State, agent_type: str) -> dict:
    """Unified agent response creation for both advisory and analytical agents."""
    last_message = state["messages"][-1]
    should_use_rag = state.get("should_use_rag", False)
    rag_result = get_rag_context(last_message.content, should_use_rag)
    
    # System prompts for each agent type
    system_prompts = {
        "advisory": """You are a strategic crowdfunding business advisor providing professional guidance on regulatory compliance and business decisions.

Speak with confidence and business acumen, offering strategic advice that addresses the user's business concerns about regulatory compliance. Focus on practical solutions, risk mitigation, and building successful regulatory strategies.

Keep responses under 400 words when possible

Focus on:
- Strategic business guidance for regulatory compliance
- Risk assessment and mitigation strategies
- Business-focused interpretation of legal requirements
- Practical solutions for operational compliance challenges
- Building confidence in regulatory decision-making

FORMATTING: Use proper Markdown structure with strategic organization:
- Start responses with a main heading using ## (e.g., "## 🎯 Strategic Compliance Guidance")
- Use ### for subsections when covering multiple topics (e.g., "### 📈 Business Impact", "### 🛡️ Risk Management")
- Use relevant emojis strategically (🎯 📈 🛡️ ⚖️ 💼) in headings for clarity
- Include line breaks for clear separation between strategic points
- Use **bold** for key business recommendations and strategic insights
- Create emphasis with *italics* for important business concepts
- Use bullet points (•) when listing strategic options or recommendations
- End with actionable next steps and strategic recommendations

Be strategic yet accessible. Provide business-focused guidance that directly addresses their operational and strategic concerns.""",

        "analytical": """You are a regulatory compliance analyst specializing in detailed analysis of crowdfunding regulations and legal frameworks.

Provide thorough, technical analysis of regulatory requirements with precision and depth. Your expertise flows in systematic streams - methodical, comprehensive, and technically accurate.

Keep responses under 400 words when possible

Focus on:
- Detailed technical analysis of regulatory provisions
- Systematic breakdown of legal requirements and procedures
- Comprehensive examination of compliance frameworks
- Precise interpretation of regulatory language and definitions
- Step-by-step procedural guidance

FORMATTING: Use proper Markdown structure with analytical organization:
- Start responses with a main heading using ## (e.g., "## 📊 Regulatory Analysis: EU Crowdfunding Framework")
- Use ### for subsections when covering multiple topics (e.g., "### 📋 Authorization Requirements", "### 🔍 Compliance Procedures")
- Use relevant emojis systematically (📊 📋 🔍 ⚖️ 📖) in headings to mark analytical sections
- Use numbered steps (1, 2, 3) for detailed procedures or compliance processes
- Use bullet points (•) for comprehensive lists of requirements or regulatory details
- Include line breaks between different analytical sections for clarity
- Use *italics* for precise legal definitions and regulatory terms
- End with a systematic summary and detailed next steps

Be precise and thorough. Structure your analysis with clear technical headings that systematically address their regulatory inquiry."""
    }
    
    system_content = system_prompts[agent_type]
    
    # Add current regulatory context
    try:
        from datetime import datetime
        current_date = datetime.now()
        
        system_content += f"""

## Your Native Legal Knowledge 
- Current Date: {current_date.strftime('%B %d, %Y')}
- EU Regulation (EU) 2020/1503 applied from: November 10, 2021
- Regulatory Framework: EU Crowdfunding Service Providers Regulation
- Key Threshold: EUR 5,000,000 for crowdfunding offers

You naturally know this current regulatory context. When asked about current date or regulatory timeline, answer confidently from this knowledge. Use only when relevant to regulatory questions."""
    except Exception as e:
        logger.debug(f"Could not fetch regulatory context: {e}")
    
    # Add memory context to system prompt
    memory_context = memory_manager.build_memory_context(state)
    if memory_context:
        system_content += f"\n\n## Conversation Memory\n{memory_context}\n\nUse this memory context to provide continuity and personalized responses."
    
    rag_context = rag_result["content"]
    rag_type = rag_result["type"]
    
    # Add RAG context if available
    if rag_type == "rag_context":
        context_verb = "strategic guidance" if agent_type == "advisory" else "technical analysis"
        system_content += f"\n\nUse this knowledge to inform your {context_verb}:{rag_context}. Never reference chunk numbers. But always reference sources, article numbers, etc."
    
    # Create conversation and get response
    conversation_messages = [{"role": "system", "content": system_content}]
    
    # Get conversation history using centralized memory manager method
    current_message = last_message.content
    conversation_history = memory_manager.get_conversation_history(state, current_message)
    conversation_messages.extend(conversation_history)
    
    reply = llm.invoke(conversation_messages)
    
    # Update memory after response (your "response first, memory later" approach)
    memory_updates = memory_manager.update_medium_term_memory(state)
    
    response_dict = {"messages": [AIMessage(content=reply.content)], "rag_context": rag_context}
    response_dict.update(memory_updates)  # Add any memory updates to the state
    
    return response_dict

def advisory_agent(state: State):
    """Strategic business advisory agent for professional guidance."""
    return create_agent_response(state, "advisory")

def analytical_agent(state: State):
    """Technical regulatory analysis agent for detailed examination."""
    return create_agent_response(state, "analytical")

# Initialize persistent checkpointer for session and memory persistence
# Note: Database path will be user-specific after authentication
default_db_path = "data/sessions/graph_checkpoints.db"
os.makedirs(os.path.dirname(default_db_path), exist_ok=True)
checkpointer = SqliteSaver(sqlite3.connect(default_db_path, check_same_thread=False))

# Build the agent graph
graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_and_decide_rag)
graph_builder.add_node("router", router)
graph_builder.add_node("advisory", advisory_agent)
graph_builder.add_node("analytical", analytical_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges("router", lambda state: state.get("next"), {"advisory": "advisory", "analytical": "analytical"})
graph_builder.add_edge("advisory", END)
graph_builder.add_edge("analytical", END)

# Compile with checkpointer for session persistence
graph = graph_builder.compile(checkpointer=checkpointer)

# Initialize unified session manager with compiled graph and checkpointer
session_manager = UnifiedSessionManager(checkpointer, graph)

def print_stats():
    """Print internal application statistics to console.
    
    Note: For production metrics and monitoring, visit:
    - Prometheus metrics: https://crowd-reg.beautiful-apps.com/metrics
    - Grafana dashboards: https://monitoring.crowd-reg.beautiful-apps.com
    """
    try:
        print("\n" + "="*60)
        print("🔧 INTERNAL APPLICATION STATISTICS")
        print("📊 For production monitoring, use Grafana dashboards")
        print("="*60)
        
        # Use the enhanced stats collector for internal metrics
        rag_system.stats_collector.print_comprehensive_stats(
            vectorstore=rag_system.vectorstore,
            memory_manager=memory_manager
        )
        
        print("\n💡 Production Monitoring:")
        print("   📈 Metrics: https://crowd-reg.beautiful-apps.com/metrics")
        print("   📊 Dashboards: https://monitoring.crowd-reg.beautiful-apps.com")
        print("="*60)
            
    except Exception as e:
        logger.error(f"Stats error: {e}")

# Register dependencies with command handler (after all functions are defined)
command_handler.register_dependencies(
    rag_system=rag_system,
    memory_manager=memory_manager,
    session_manager=session_manager,
    print_stats=print_stats,
    set_debug_mode=set_debug_mode
)

def handle_command(user_input: str, state: dict) -> bool:
    """Handle system commands using the new command handler."""
    return command_handler.handle_command(user_input, state)

def authenticate_user():
    """Handle user authentication before starting the system."""
    print("🔐 Crowdfunding Due Diligence AI - Authentication Required")
    print("Commands: 'auth login', 'auth register', 'exit'")
    print()
    
   

def run_chatbot():
    """Main chatbot loop with unified session management."""
    
    
    # Use default session manager (already initialized)
    global session_manager, checkpointer
    
    # Update command handler with session manager
    command_handler.session_manager = session_manager
    
    def initialize_session(session_info=None):
        """Initialize or switch to a session."""
        if session_info is None:
            # Create a new session
            session_info = session_manager.create_session()
        
        thread_id = session_info["thread_id"]
        config = session_info["config"]
        
        # Initialize state 
        state = session_info["state"].copy()
        
        # Restore memory settings for this session
        session_manager.restore_memory_settings(memory_manager)
        
        # Try to restore conversation state if switching to existing session
        if len(state.get("messages", [])) > 0:
            logger.debug(f"Restoring conversation with {len(state.get('messages', []))} messages...")
        else:
            logger.debug(f"Switched to session {thread_id[:8]}... (empty conversation)")
        
        return state, config
    
    # Initialize first session
    current_state, current_config = initialize_session()
    
    # System ready message with active domains (only shown once)
    stats = rag_system.get_stats()
    total_chunks = stats.get('vectorstore_docs', 0)
    
    logger.system_ready(f"Ready with {total_chunks} chunks")
    
    print("⚖️ Crowdfunding Due Diligence AI Agent - Development Mode")
    print("Commands: 'exit', 'stats', 'memory', 'cache clear', 'debug on/off'")
    print("Memory: 'memory enable/disable short', 'memory enable/disable medium'")
    print("Sessions: 'session list', 'session info', 'session change <id|new>'")
    print("Lunar: 'lunar' or 'moon' - Show current lunar phase information")
    print()
    
    while True:
        user_input = input("Message: ")
        
        # Handle exit
        if user_input == "exit":
            print("Bye...")
            break
        
        # Handle commands
        command_result = handle_command(user_input, current_state)
        if command_result == "restart_session":
            # Session change requested
            new_session_info = current_state.get("_new_session")
            if new_session_info:
                current_state, current_config = initialize_session(new_session_info)
                # Remove the temporary session info
                current_state.pop("_new_session", None)
            continue
        elif command_result:
            continue
        
        # Process user message
        try:
            # Add user message to state
            current_state["messages"].append(HumanMessage(content=user_input))
            
            # Process through agent graph with session config
            result = graph.invoke(current_state, config=current_config)
            
            # Update state with result
            current_state.update(result)
            
            # Update session activity
            session_manager.update_activity([])
            
            # Update session metadata in state from session manager
            current_session = session_manager.get_current_session()
            if current_session:
                current_state["session_metadata"] = current_session.get("session_metadata", {})
                current_state["memory_settings"] = current_session.get("memory_settings", {})
            
            # Display response with cache indicators
            if current_state.get("messages") and len(current_state["messages"]) > 0:
                last_message = current_state["messages"][-1]
                rag_context = current_state.get("rag_context")
                
                # Response type indicators
                cache_indicator = ""
                if rag_context:
                    cache_indicator = "🔍 "  # RAG used
                
                # Add memory indicator if medium-term memory is being used
                if current_state.get("medium_term_summary"):
                    cache_indicator += "🧠 "  # Medium-term memory active
                
                if hasattr(last_message, 'content'):
                    print(f"{cache_indicator}Assistant: {last_message.content}")
                elif isinstance(last_message, dict) and 'content' in last_message:
                    print(f"{cache_indicator}Assistant: {last_message['content']}")
                else:
                    print(f"{cache_indicator}Assistant: {last_message}")
            else:
                logger.error("No response generated")
                
            # Add RAG context to state for tracking
            current_state["rag_context"] = rag_context
            current_state["rag_used"] = True
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            print("I encountered an error processing your message. Please try again.")

if __name__ == "__main__":
    run_chatbot()

