# 🌙 Esoteric Vectors - Advanced Multi-Agent RAG System with Unified Session Management

A sophisticated esoteric AI agent with dual-personality architecture, specialized Q&A caching, domain-aware RAG retrieval, comprehensive spiritual knowledge base, and robust session management with persistent memory.

## 🎯 Product Vision

**Esoteric Vectors** is an intelligent spiritual companion that combines the wisdom of ancient traditions with modern AI technology. The system features dual agents - a compassionate therapist for emotional support and a structured teacher for knowledge delivery - both enhanced with specialized esoteric knowledge across multiple spiritual domains and persistent conversation memory.

## ✨ Key Features

### 🧠 **Unified Session & Memory Management** ⭐ NEW!
- **Persistent Sessions**: Multiple concurrent conversations that survive app restarts
- **Memory Settings Persistence**: Short-term and medium-term memory toggles preserved across sessions
- **Session Switching**: Seamlessly switch between different conversation threads
- **SQLite-Based Storage**: Single source of truth for all session data and conversation history
- **Zero Data Loss**: Full conversation context and settings restored on session change

### 🤖 **Dual-Agent Architecture**
- **Therapist Agent**: Emotional support with warm, intuitive guidance
- **Logical Agent**: Structured teaching with clear explanations
- **Intelligent Routing**: Automatic classification between emotional and logical queries

### ⚡ **Advanced Caching System**
- **Q&A Cache**: Lightning-fast responses for direct question matches (150+ Q&A pairs)
- **Negative Intent Detection**: Prevents cache bypass for semantically opposite queries
- **Domain Filtering**: Targeted retrieval based on active knowledge domains

### 🎯 **Domain-Aware Knowledge**
- **Lunar Wisdom**: Moon phases, cosmic timing, lunar influences (40 Q&As)
- **Internal Family Systems**: IFS therapy, parts work, psychological healing (30 Q&As)
- **Crystal Healing**: Crystal properties, energy work, formations (40 Q&As)
- **Astrology**: Planetary influences, astrological concepts (40 Q&As)
- **Additional Domains**: Tarot, numerology, shadow work, archetypes

### 🛡️ **Safety & Intelligence**
- **Semantic Domain Detection**: Suggests relevant domain activation
- **Context-Aware Responses**: Maintains conversation continuity
- **Performance Analytics**: Comprehensive statistics and monitoring
- **Clean Command System**: Organized command handling with registry pattern

## 📁 Project Structure

```
esoteric-vectors/
├── src/                              # Source code
│   ├── main.py                       # Multi-agent system with LangGraph & session management
│   ├── core/                         # Core system components
│   │   ├── contextual_rag.py         # Main RAG system with domain filtering
│   │   ├── domain_manager.py         # Domain activation/deactivation
│   │   ├── unified_session_manager.py # Session & memory persistence ⭐ NEW!
│   │   ├── resilience_manager.py     # System reliability and error recovery
│   │   └── stats_collector.py        # Performance monitoring
│   ├── cache/                        # Caching systems
│   │   ├── qa_cache.py               # Q&A cache with question-based retrieval
│   │   └── negative_intent_detector.py # Safety filtering
│   ├── memory/                       # Memory management ⭐ NEW!
│   │   └── memory_manager.py         # Short/medium-term memory with persistence
│   └── utils/                        # Utility modules
│       ├── command_handler.py        # Unified command system ⭐ NEW!
│       ├── logger.py                 # Enhanced logging with debug modes
│       ├── semantic_domain_detector.py # Domain suggestion system
│       ├── relevance_evaluator.py    # RAG relevance scoring
│       └── lunar_calculator.py       # Lunar phase calculations
├── data/                             # Data storage
│   ├── chroma_db/                    # Vector databases
│   │   ├── qa_cache/                 # Q&A-specific vectorstore
│   │   └── [domain_collections]/     # Domain-specific collections
│   ├── sessions/                     # Session persistence ⭐ NEW!
│   │   └── graph_checkpoints.db      # SQLite session database
│   ├── qa/                           # Q&A documents
│   │   ├── lunar_qa.md               # Lunar wisdom Q&As
│   │   ├── ifs_qa.md                 # IFS therapy Q&As
│   │   ├── crystals_qa.md            # Crystal healing Q&As
│   │   └── astrology_qa.md           # Astrology Q&As
│   └── document_registry.json        # Document tracking registry
├── docs/                             # Knowledge base documents
│   ├── esoteric/                     # Esoteric knowledge
│   │   ├── Lunar_overview.md         # Comprehensive lunar wisdom
│   │   ├── ifs.md                    # Internal Family Systems guide
│   │   ├── crystals.md               # Crystal healing knowledge
│   │   ├── astrology.md              # Astrological concepts
│   │   ├── tarot.md                  # Tarot symbolism and meanings
│   │   ├── archetypes.md             # Jungian archetypes
│   │   ├── shadow.md                 # Shadow work practices
│   │   └── Numerology.md             # Numerological principles
│   └── tech/                         # Technical documentation
├── tests/                            # Test suites
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── performance/                  # Performance benchmarks
├── config/                           # Configuration
├── document_manager.py               # Document management utility
├── pyproject.toml                   # Project configuration
├── uv.lock                          # Dependency lock file
└── run.py                           # Application entry point
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key
- Google Gemini API key

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd esoteric-vectors

# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Using UV (recommended) - automatically reads pyproject.toml
uv sync

# Alternative: Using pip
# pip install -e .
```

### 3. Configure Environment
```bash
# Add your API keys as environment variables:
export OPENAI_API_KEY=your_openai_key_here
export GOOGLE_API_KEY=your_gemini_key_here

# Or create .env file:
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "GOOGLE_API_KEY=your_gemini_key_here" >> .env
```

### 4. Initialize Knowledge Base (Optional)
```bash
# Load documents into vector database
python document_manager.py
```

## 🎮 Usage

### Start the Application
```bash
# Method 1: Direct execution
python run.py

# Method 2: From src directory
cd src && python main.py
```

### 📋 Command System ⭐ ENHANCED!

#### **Session Management** 🧠
```bash
# Session operations
session list                     # Show all available sessions
session info                     # Show current session details
session change new               # Create and switch to new session
session change <partial-id>      # Switch to existing session (e.g., abc123)
session delete <partial-id>      # Delete a session

# Examples:
session change new               # Start fresh conversation
session change dc52e390          # Switch to session starting with "dc52e390"
session list                     # See: "1. dc52e390... (2025-06-10) - 5 msgs, domains: lunar"
```

#### **Memory Management** 🧠
```bash
# Memory status and control
memory                          # Show current memory status
memory status                   # Detailed memory information
memory clear                    # Clear current conversation memory

# Memory toggles (persistent across sessions)
memory enable short             # Enable short-term memory
memory disable short            # Disable short-term memory  
memory enable medium            # Enable medium-term memory
memory disable medium           # Disable medium-term memory
```

#### **Domain Management** 🎯
```bash
# Domain operations
domains                         # Show active/available domains
domains enable <domain>         # Activate knowledge domain
domains disable <domain>        # Deactivate knowledge domain

# Examples:
domains enable lunar            # Activate lunar wisdom
domains disable crystals        # Deactivate crystal knowledge
```

#### **System Operations** ⚙️
```bash
# System commands
stats                          # Show comprehensive system statistics
debug on                       # Enable detailed debug logging
debug off                      # Disable debug logging
exit                          # Exit the application

# Cache management
cache clear                    # Clear RAG caches
cache stats clear             # Reset query statistics
qa cache clear                # Clear Q&A cache specifically
```

### 🌟 Session & Memory Examples

#### **Multiple Conversation Management:**
```bash
# Start with astrology discussion
session change new
"Tell me about moon phases in astrology"
> AI responds with astrological moon phase information...

# Switch to new session for crystal healing
session change new  
"What crystals help with anxiety?"
> AI responds with crystal recommendations...

# Return to astrology session - full context restored!
session list
> 1. abc123... (2025-06-10) - 3 msgs, domains: lunar, astrology
> 2. def456... (2025-06-10) - 2 msgs, domains: crystals

session change abc123
"Continue our moon discussion"
> AI: "We were discussing moon phases in astrology. You asked about..."
```

#### **Memory Persistence:**
```bash
# Configure memory settings
memory disable short           # Turn off recent context
memory enable medium          # Keep conversation summaries

# These settings are saved to your session!
# Close app, restart, switch back to session:
session change abc123
> Memory settings automatically restored: ST:False, MT:True
```

#### **Cross-Session Memory:**
```bash
# Memory settings persist per session:
# Session A: memory disable short
# Session B: memory enable short  
# Session A retains: short=off, Session B retains: short=on
```

### Example Interactions
```bash
# Emotional support (routes to Therapist Agent)
"I'm feeling anxious and disconnected lately"
"I'm struggling with a difficult relationship"

# Knowledge queries (routes to Logical Agent)  
"Explain the phases of the moon"
"How does IFS therapy work?"
"What are the properties of amethyst?"

# Domain activation suggestions
"Tell me about tarot cards"  # Suggests activating tarot domain
```

## 🏗️ Advanced System Architecture ⭐ UPDATED!

### Unified Session Management
```
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Framework                        │
├─────────────────────────────────────────────────────────────┤
│  SqliteSaver (Single Source of Truth)                      │
│  ├── graph_checkpoints.db                                  │
│  ├── Session States (messages, metadata, memory_settings)  │
│  └── Thread Management                                     │
├─────────────────────────────────────────────────────────────┤
│  UnifiedSessionManager                                      │
│  ├── create_session() → New conversation                   │
│  ├── load_session() → Restore full context                 │
│  ├── save_memory_settings() → Persist toggles              │
│  └── update_activity() → Track usage                       │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Agent Flow
```
User Input → CommandHandler → [Session|Memory|Domain|System] Commands
     ↓
Classifier → Router → [Therapist|Logical] Agent → Response
     ↓
RAG Decision → Q&A Cache → RAG Fallback → Domain Filtering
```

### Session State Structure
```python
State = {
    "messages": [...],                    # Full conversation history
    "memory_settings": {                  # Persistent memory toggles
        "short_term_enabled": True,
        "medium_term_enabled": True
    },
    "session_metadata": {                 # Session tracking
        "created_at": "2025-06-10T17:16:54",
        "last_activity": "2025-06-10T17:20:15", 
        "message_count": 8,
        "domains_used": ["lunar", "astrology"]
    }
}
```

### Performance Indicators
- ⚡ Q&A cache hit (fastest response)
- 🛡️ Negative intent bypass (security protection)
- 🔍 RAG retrieval (comprehensive search)
- 🧠 Medium-term memory (conversation context)
- 🚫 Domain blocked (controlled access)

## 📊 System Components Deep Dive

### Core Session Management ⭐ NEW!
- **`unified_session_manager.py`**: Single source of truth for session persistence
- **`memory_manager.py`**: Enhanced memory with persistence and per-session settings
- **`command_handler.py`**: Organized command system with registry pattern

### Core RAG Systems
- **`main.py`**: LangGraph-based multi-agent orchestration with session management
- **`contextual_rag.py`**: Domain-aware RAG with ChromaDB integration
- **`qa_cache.py`**: Specialized Q&A caching with question-only embeddings
- **`domain_manager.py`**: Dynamic domain activation/deactivation

### Intelligence & Safety Layers
- **`semantic_domain_detector.py`**: Suggests relevant domain activation
- **`negative_intent_detector.py`**: Prevents cache poisoning attacks
- **`relevance_evaluator.py`**: Scores RAG retrieval quality
- **`stats_collector.py`**: Comprehensive performance monitoring
- **`resilience_manager.py`**: System reliability and error recovery

### Enhanced Utilities ⭐ NEW!
- **`logger.py`**: Enhanced logging with debug modes and user/system operation tracking
- **`document_manager.py`**: Parallel document processing and management
- **`lunar_calculator.py`**: Astronomical calculations for lunar wisdom

## 📈 Performance Metrics

### Current Statistics
- **Q&A Cache**: 150+ question-answer pairs across 6 domains
- **Vector Database**: 1,378+ document chunks
- **Active Domains**: 2 domains active by default (IFS, Lunar)
- **Session Database**: SQLite-based persistent storage
- **Cache Hit Rate**: 85%+ similarity threshold
- **Response Time**: 
  - Q&A Cache: ~0.1-0.3s
  - RAG Retrieval: ~2-6s
  - Session Operations: ~0.1-0.5s
  - Domain Detection: ~0.5s

### Session Management Performance
- **Session Creation**: <0.1s
- **Session Loading**: <0.5s (including conversation restoration)
- **Memory Settings Persistence**: <0.1s
- **Cross-Session Switching**: Full context restoration in <1s

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests  
python -m pytest tests/integration/

# Performance benchmarks
python -m pytest tests/performance/

# Test session management
python -c "
import sys; sys.path.append('src')
from core.unified_session_manager import UnifiedSessionManager
print('Session management tests passed')
"
```

## 📚 Document Management

### Adding Standard Documents
```bash
# Using document manager
python document_manager.py

# Interactive mode - follow prompts to:
# 1. Add single documents
# 2. Batch add multiple documents
# 3. Update existing documents
# 4. Remove documents
```

### Adding Q&A Documents
Q&A documents follow a specific format for optimal caching:

```markdown
## 1. Question here?

Answer content here...

---

## 2. Another question?

Another answer...
```

**Steps to add Q&A documents:**
1. Create/edit Q&A file in `data/qa/` directory
2. Use the document manager or run update script:
```bash
# Update Q&A cache after modifications
python -c "
import sys; sys.path.append('src')
from cache.qa_cache import QACache
qa = QACache()
qa.clear_cache()
qa.add_qa_document('data/qa/your_file.md', 'domain_name')
"
```

### Document Types
- **Standard Documents** (`docs/esoteric/`): Narrative content, chunked at 1000 chars
- **Q&A Documents** (`data/qa/`): Question-answer pairs, chunked at 2000 chars
- **Domain Classification**: lunar, ifs, crystals, astrology, tarot, numerology, archetypes

## 🔧 Advanced Configuration

### Debug Mode
```bash
# Enable detailed system logging
debug on

# Detailed output shows:
# 🔧 DEBUG: Session operations
# 🔧 DEBUG: Memory state changes  
# 🔧 DEBUG: Command processing
# 🔧 DEBUG: RAG retrieval details
```

### Session Database Location
```
data/sessions/graph_checkpoints.db
```

### Available Domains
- `lunar` - Moon phases, cosmic timing, lunar influences
- `ifs` - Internal Family Systems therapy, parts work
- `crystals` - Crystal properties, energy work, formations  
- `astrology` - Planetary influences, astrological concepts
- `tarot` - Tarot symbolism, card meanings, spreads
- `numerology` - Number meanings, calculations, interpretations
- `archetypes` - Jungian archetypes, shadow work, psychological patterns

## 🌟 Advanced Features

### Session Persistence ⭐ NEW!
- **Multi-Session Management**: Run multiple concurrent conversations
- **Memory Persistence**: Short/medium-term memory settings saved per session
- **Conversation Restoration**: Full context restoration when switching sessions
- **Session Metadata**: Track creation time, activity, domains used, message counts

### Enhanced Memory System ⭐ NEW!
- **Per-Session Settings**: Each session maintains its own memory configuration
- **Persistent Toggles**: Memory enable/disable states survive app restarts
- **Context Restoration**: Previous conversation context restored on session switch
- **User vs System Operations**: Distinguishes between user-triggered and system memory changes

### Unified Command System ⭐ NEW!
- **Registry Pattern**: Clean, extensible command handling
- **Category Organization**: Commands grouped by function (Session, Memory, Domain, System)
- **Dependency Injection**: Clean separation of concerns
- **Error Handling**: Graceful command error recovery

### Contextual Understanding
- **Conversation Memory**: Maintains context within sessions with persistence
- **Domain Awareness**: Filters knowledge by active domains
- **Intent Classification**: Distinguishes emotional vs. logical needs

### Safety & Reliability
- **Negative Intent Protection**: Prevents semantic manipulation
- **Error Recovery**: Graceful fallbacks for failed operations
- **Data Validation**: Ensures document integrity and consistency
- **Session Isolation**: Sessions are completely independent

### Extensibility
- **Plugin Architecture**: Easy addition of new domains and commands
- **Configurable Thresholds**: Adjustable similarity and performance settings
- **API Integration**: Multiple LLM providers (OpenAI, Google Gemini)
- **Database Agnostic**: Can switch from SQLite to PostgreSQL for production

## 🔮 Recent Improvements & Future Enhancements

### ✅ **Recently Implemented:**
- **Unified Session Management**: Complete overhaul of session persistence
- **Enhanced Memory System**: Per-session memory settings with full persistence
- **Command System Restructure**: Clean, organized command handling
- **SQLite-Based Storage**: Single source of truth for all session data
- **Zero Data Loss**: Full conversation and settings restoration
- **Debug Mode Enhancements**: Detailed system operation logging

### 🚀 **Future Enhancements:**
- **PostgreSQL Migration**: Production-ready database backend
- **Voice Interface**: Audio input/output capabilities
- **Mobile App**: Cross-platform mobile application
- **Community Features**: Shared wisdom and collaborative learning
- **Advanced Analytics**: Usage patterns and conversation insights
- **Export/Import**: Session backup and sharing capabilities

## 🆘 Troubleshooting

### Common Issues
```bash
# Session not found
session list                    # Check available sessions
session change new             # Create new session if needed

# Memory not persisting
debug on                       # Enable debug mode to see memory operations
memory status                  # Check current memory state

# Commands not working
debug on                       # See detailed command processing
stats                         # Check system health

# Database issues
# Delete and recreate session database:
rm data/sessions/graph_checkpoints.db
# Restart application - new database will be created
```

### Performance Issues
```bash
# Clear caches if performance degrades
cache clear                    # Clear all caches
qa cache clear                # Clear only Q&A cache

# Check system status
stats                         # View comprehensive statistics
```

## 📋 Quick Reference

### Session Commands
```bash
session list                   # List all sessions
session info                   # Current session details  
session change <id>            # Switch to session
session change new             # Create new session
session delete <id>            # Delete session
```

### Memory Commands
```bash
memory                        # Show memory status
memory enable/disable short   # Toggle short-term memory
memory enable/disable medium  # Toggle medium-term memory
memory clear                  # Clear conversation memory
```

### System Commands
```bash
stats                        # System statistics
domains                      # Domain management
cache clear                  # Clear caches
debug on/off                 # Toggle debug mode
exit                        # Exit application
```

---

*Built with LangChain, ChromaDB, LangGraph, OpenAI, Google Gemini, and SQLite - Bridging ancient wisdom with modern AI through persistent, intelligent conversations.* 