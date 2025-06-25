# 🏛️ Crowd Due Dill - Advanced AI Agent for Crowdfunding Regulation & Legal Compliance

A sophisticated AI-powered legal compliance assistant specializing in crowdfunding regulations, with dual-agent architecture, domain-aware RAG retrieval, comprehensive regulatory knowledge base, and robust session management with persistent memory.

## 🎯 Product Vision

**Crowd Due Dill** is an intelligent legal companion that combines expertise in crowdfunding regulations with modern AI technology. The system features dual agents - a strategic advisory agent for business guidance and an analytical agent for technical legal analysis - both enhanced with specialized knowledge across multiple regulatory domains and persistent conversation memory.

## ✨ Key Features

### 🧠 **Unified Session & Memory Management** ⭐ NEW!
- **Persistent Sessions**: Multiple concurrent legal consultations that survive app restarts
- **Memory Settings Persistence**: Short-term and medium-term memory toggles preserved across sessions
- **Session Switching**: Seamlessly switch between different regulatory consultation threads
- **SQLite-Based Storage**: Single source of truth for all session data and legal conversation history
- **Zero Data Loss**: Full consultation context and settings restored on session change

### 🤖 **Dual-Agent Architecture**
- **Advisory Agent**: Strategic business guidance on regulatory compliance and risk management
- **Analytical Agent**: Technical legal analysis with detailed regulatory breakdowns
- **Intelligent Routing**: Automatic classification between business strategy and legal analysis queries

### ⚡ **Advanced Caching System**
- **Q&A Cache**: Lightning-fast responses for common regulatory questions
- **Negative Intent Detection**: Prevents cache bypass for semantically opposite queries
- **Domain Filtering**: Targeted retrieval based on active regulatory domains

### 🎯 **Domain-Aware Regulatory Knowledge**
- **EU Crowdfunding Regulation**: Complete EU Regulation 2020/1503 coverage
- **Securities Law**: Investment regulations, prospectus requirements, investor protection
- **Compliance Requirements**: Authorization procedures, prudential requirements, risk management
- **Cross-Border Services**: Passporting rights, regulatory harmonization, ESMA guidelines
- **Due Diligence**: Platform requirements, project owner verification, ongoing compliance

### 🛡️ **Safety & Intelligence**
- **Context-Aware Responses**: Maintains legal consultation continuity
- **Performance Analytics**: Comprehensive statistics and monitoring
- **Clean Command System**: Organized command handling with registry pattern
- **Single Domain Focus**: Specialized in EU crowdfunding regulations for optimal accuracy

### 🕷️ **Web Crawler** (Optional Component)
- **Content Extraction**: Intelligent web crawling with LLM-readable markdown conversion
- **Multiple Strategies**: Single page, batch crawling, sitemap parsing, and query-focused extraction
- **Content Filtering**: PruningContentFilter and BM25 filtering for high-quality content
- **Database Integration**: Direct addition of crawled content to the knowledge base

## 📁 Project Structure

```
crowd-due-dill/
├── src/                              # Source code
│   ├── main.py                       # Multi-agent system with LangGraph & session management
│   ├── core/                         # Core system components
│   │   ├── contextual_rag.py         # Main RAG system with domain filtering
│   │   ├── domain_manager.py         # Simplified single-domain manager (eu_crowdfunding)
│   │   ├── unified_session_manager.py # Session & memory persistence ⭐ NEW!
│   │   ├── resilience_manager.py     # System reliability and error recovery
│   │   ├── stats_collector.py        # Performance monitoring
│   │   ├── auth0_middleware.py       # Authentication and user management
│   │   └── stripe_service.py         # Premium subscription management
│   ├── cache/                        # Caching systems
│   │   ├── qa_cache.py               # Q&A cache with question-based retrieval
│   │   └── negative_intent_detector.py # Safety filtering
│   ├── memory/                       # Memory management ⭐ NEW!
│   │   └── memory_manager.py         # Short/medium-term memory with persistence
│   └── utils/                        # Utility modules
│       ├── command_handler.py        # Unified command system ⭐ NEW!
│       ├── logger.py                 # Enhanced logging with debug modes
│       └── resilience.py             # System resilience utilities
├── data/                             # Data storage
│   ├── chroma_db/                    # Vector databases
│   │   ├── qa_cache/                 # Q&A-specific vectorstore
│   │   └── [domain_collections]/     # Domain-specific collections
│   ├── sessions/                     # Session persistence ⭐ NEW!
│   │   └── graph_checkpoints.db      # SQLite session database
│   └── document_registry.json        # Document tracking registry
├── docs/                             # Legal knowledge base documents
│   ├── content/                      # Regulatory content
│   │   └── main_eu_regulation.md     # EU Crowdfunding Regulation 2020/1503
│   └── tech/                         # Technical documentation
│       ├── GDPR_gd.md                # GDPR compliance guidance for AI systems
│       ├── security.md               # AI security frameworks and compliance
│       └── [other technical docs]    # System architecture and compliance docs
├── tests/                            # Test suites
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── performance/                  # Performance benchmarks
├── web/                              # Web interface
│   ├── index.html                    # Main web application
│   ├── components/                   # React components
│   ├── services/                     # Frontend services (Auth0, Stripe)
│   └── config/                       # Frontend configuration
├── config/                           # Configuration
├── tools/                            # Management tools
│   ├── document_manager.py           # Document management utility
│   └── web_crawler.py               # Web crawler for content extraction (optional)
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
- Auth0 account (for web interface)
- Stripe account (for premium features)

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd crowd-due-dill

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
# Load regulatory documents into vector database
python tools/document_manager.py
```

## 🎮 Usage

### Start the Application
```bash
# Method 1: Direct execution
python run.py

# Method 2: From src directory
cd src && python main.py

# Method 3: Web interface (requires web setup)
python start_web_api.py
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
session change new               # Start fresh legal consultation
session change dc52e390          # Switch to session starting with "dc52e390"
session list                     # See: "1. dc52e390... (2025-06-10) - 5 msgs, domains: eu_crowdfunding"
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
# Domain information
domains                         # Show current domain status (always eu_crowdfunding)

# Note: Domain switching is disabled in single-domain mode
# The system is optimized for EU crowdfunding regulations only
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

#### **Multiple Legal Consultation Management:**
```bash
# Start with EU regulation discussion
session change new
"What are the authorization requirements for crowdfunding platforms?"
> AI responds with detailed EU Regulation 2020/1503 requirements...

# Switch to new session for compliance discussion
session change new  
"How should we structure our due diligence procedures?"
> AI responds with compliance framework recommendations...

# Return to regulation session - full context restored!
session list
> 1. abc123... (2025-06-10) - 3 msgs, domains: eu_crowdfunding
> 2. def456... (2025-06-10) - 2 msgs, domains: compliance

session change abc123
"Continue our authorization discussion"
> AI: "We were discussing authorization requirements. You asked about..."
```

#### **Memory Persistence:**
```bash
# Configure memory settings
memory disable short           # Turn off recent context
memory enable medium          # Keep consultation summaries

# These settings are saved to your session!
# Close app, restart, switch back to session:
session change abc123
> Memory settings automatically restored: ST:False, MT:True
```

### Example Interactions
```bash
# Business strategy queries (routes to Advisory Agent)
"What are the business risks of cross-border crowdfunding?"
"How should we structure our platform to ensure compliance?"

# Legal analysis queries (routes to Analytical Agent)  
"Explain Article 12 of EU Regulation 2020/1503"
"What are the prudential requirements for crowdfunding platforms?"
"How does the €5M threshold work for offerings?"

# Domain activation suggestions
"Tell me about MiFID II requirements"  # Suggests activating securities law domain
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
│  ├── create_session() → New consultation                   │
│  ├── load_session() → Restore full context                 │
│  ├── save_memory_settings() → Persist toggles              │
│  └── update_activity() → Track usage                       │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Agent Flow
```
User Input → CommandHandler → [Session|Memory|Domain|System] Commands
     ↓
Classifier → Router → [Advisory|Analytical] Agent → Response
     ↓
RAG Decision → Q&A Cache → RAG Fallback → Domain Filtering
```

### Session State Structure
```python
State = {
    "messages": [...],                    # Full consultation history
    "memory_settings": {                  # Persistent memory toggles
        "short_term_enabled": True,
        "medium_term_enabled": True
    },
    "session_metadata": {                 # Session tracking
        "created_at": "2025-06-10T17:16:54",
        "last_activity": "2025-06-10T17:20:15", 
        "message_count": 8,
        "domains_used": ["eu_crowdfunding", "compliance"]
    }
}
```

### Performance Indicators
- ⚡ Q&A cache hit (fastest response)
- 🛡️ Negative intent bypass (security protection)
- 🔍 RAG retrieval (comprehensive regulatory search)
- 🧠 Medium-term memory (consultation context)
- 🚫 Domain blocked (controlled access)

## 📊 System Components Deep Dive

### Core Session Management ⭐ NEW!
- **`unified_session_manager.py`**: Single source of truth for session persistence
- **`memory_manager.py`**: Enhanced memory with persistence and per-session settings
- **`command_handler.py`**: Organized command system with registry pattern

### Core RAG Systems
- **`main.py`**: LangGraph-based multi-agent orchestration with session management
- **`contextual_rag.py`**: Domain-aware RAG with ChromaDB integration
- **`qa_cache.py`**: Specialized Q&A caching for regulatory questions
- **`domain_manager.py`**: Simplified single-domain manager for EU crowdfunding regulations

### Intelligence & Safety Layers
- **`negative_intent_detector.py`**: Prevents cache poisoning attacks
- **`stats_collector.py`**: Comprehensive performance monitoring
- **`resilience_manager.py`**: System reliability and error recovery

### Authentication & Premium Features
- **`auth0_middleware.py`**: User authentication and management
- **`stripe_service.py`**: Premium subscription handling

### Enhanced Utilities ⭐ NEW!
- **`logger.py`**: Enhanced logging with debug modes and legal operation tracking
- **`document_manager.py`**: Parallel document processing and management

## 📈 Performance Metrics

### Current Statistics
- **Regulatory Knowledge**: Complete EU Crowdfunding Regulation 2020/1503
- **Vector Database**: 1,400+ regulatory document chunks
- **Active Domains**: EU crowdfunding regulation domain active by default
- **Session Database**: SQLite-based persistent storage
- **Cache Hit Rate**: 85%+ similarity threshold
- **Response Time**: 
  - Q&A Cache: ~0.1-0.3s
  - RAG Retrieval: ~2-6s
  - Session Operations: ~0.1-0.5s
  - Regulatory Analysis: ~0.5-2s

### Session Management Performance
- **Session Creation**: <0.1s
- **Session Loading**: <0.5s (including consultation restoration)
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

### Adding Regulatory Documents
```bash
# Using document manager
python tools/document_manager.py

# Interactive mode - follow prompts to:
# 1. Add single documents
# 2. Batch add multiple documents
# 3. Update existing documents
# 4. Remove documents
```

## 🕷️ Web Crawler (Optional Component)

The web crawler allows you to extract content from websites and add it to the knowledge base in LLM-readable markdown format.

### Installation
```bash
# Install crawler dependencies
pip install -r config/requirements_crawler.txt
playwright install

# Test installation
python tools/test_web_crawler.py
```

### Basic Usage
```bash
# Crawl a single page
python tools/web_crawler.py https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32020R1503

# Crawl multiple pages
python tools/web_crawler.py --batch url1 url2 url3

# Query-focused crawling (extract GDPR-related content)
python tools/web_crawler.py https://example.com --query "GDPR data protection privacy"

# Add crawled content to database
python tools/web_crawler.py https://example.com --add-to-db --domain "regulatory_docs"

# Get help
python tools/web_crawler.py --help
```

### Advanced Features
- **Content Filtering**: Removes ads, navigation, and low-value content
- **Query-Focused Extraction**: BM25 filtering for topic-relevant content
- **Sitemap Support**: Crawl entire websites from sitemap.xml
- **Batch Processing**: Parallel crawling with configurable concurrency
- **Database Integration**: Direct addition to Crowd Due Dill knowledge base

For detailed usage examples and API documentation, see [`tools/README_WebCrawler.md`](tools/README_WebCrawler.md).

### Document Types
- **Regulatory Documents** (`docs/content/`): Legal texts, regulations, directives
- **Q&A Documents**: Regulatory question-answer pairs for fast lookup
- **Domain Classification**: eu_crowdfunding, securities_law, compliance, best_practices

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
# 🔧 DEBUG: Regulatory analysis steps
```

### Session Database Location
```
data/sessions/graph_checkpoints.db
```

### Available Regulatory Domains
- `eu_crowdfunding` - EU Crowdfunding Regulation 2020/1503, ESMA guidelines
- `securities_law` - MiFID II, Prospectus Regulation, investment services
- `compliance` - Authorization procedures, ongoing obligations, reporting
- `best_practices` - Industry standards, risk management frameworks

## 🌟 Advanced Features

### Session Persistence ⭐ NEW!
- **Multi-Session Management**: Run multiple concurrent legal consultations
- **Memory Persistence**: Short/medium-term memory settings saved per session
- **Consultation Restoration**: Full legal context restoration when switching sessions
- **Session Metadata**: Track creation time, activity, regulatory domains used, message counts

### Enhanced Memory System ⭐ NEW!
- **Per-Session Settings**: Each consultation maintains its own memory configuration
- **Persistent Toggles**: Memory enable/disable states survive app restarts
- **Context Restoration**: Previous legal consultation context restored on session switch
- **User vs System Operations**: Distinguishes between user-triggered and system memory changes

### Unified Command System ⭐ NEW!
- **Registry Pattern**: Clean, extensible command handling
- **Category Organization**: Commands grouped by function (Session, Memory, Domain, System)
- **Dependency Injection**: Clean separation of concerns
- **Error Handling**: Graceful command error recovery

### Contextual Understanding
- **Consultation Memory**: Maintains legal context within sessions with persistence
- **Domain Awareness**: Filters regulatory knowledge by active domains
- **Intent Classification**: Distinguishes strategic advisory vs. technical legal analysis needs

### Safety & Reliability
- **Negative Intent Protection**: Prevents semantic manipulation
- **Error Recovery**: Graceful fallbacks for failed operations
- **Data Validation**: Ensures regulatory document integrity and consistency
- **Session Isolation**: Legal consultations are completely independent

### Web Interface & Premium Features
- **React Frontend**: Modern web interface for legal consultations
- **Auth0 Integration**: Secure user authentication and management
- **Stripe Integration**: Premium subscription management
- **Mobile Responsive**: Cross-platform accessibility

## 🔮 Recent Improvements & Future Enhancements

### ✅ **Recently Implemented:**
- **Unified Session Management**: Complete overhaul of session persistence
- **Enhanced Memory System**: Per-session memory settings with full persistence
- **Command System Restructure**: Clean, organized command handling
- **SQLite-Based Storage**: Single source of truth for all session data
- **Zero Data Loss**: Full consultation and settings restoration
- **Debug Mode Enhancements**: Detailed legal operation logging

### 🚀 **Future Enhancements:**
- **Additional Regulatory Domains**: National crowdfunding laws, international frameworks
- **Document Compliance Checker**: Automated compliance verification for legal documents
- **Regulatory Updates Tracker**: Real-time monitoring of regulatory changes
- **Multi-Language Support**: Support for multiple EU languages
- **Advanced Analytics**: Usage patterns and consultation insights
- **Export/Import**: Session backup and sharing capabilities
- **API Integration**: RESTful API for third-party integrations

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
memory clear                  # Clear consultation memory
```

### System Commands
```bash
stats                        # System statistics
domains                      # Regulatory domain management
cache clear                  # Clear caches
debug on/off                 # Toggle debug mode
exit                        # Exit application
```

## 🏛️ Legal & Compliance

This system is designed to assist with regulatory compliance research and analysis. It does not constitute legal advice and should not be used as a substitute for professional legal counsel. Always consult qualified legal professionals for specific regulatory compliance decisions.

---

*Built with LangChain, ChromaDB, LangGraph, OpenAI, Google Gemini, Auth0, Stripe, and SQLite - Bridging regulatory expertise with modern AI for intelligent legal compliance assistance.*
