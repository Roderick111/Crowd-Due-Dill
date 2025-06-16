# **Medium-Term Memory Design**

## **1. Overview**

Medium-term memory provides intra-conversational context continuity within a single session. When conversations exceed the 10-message short-term memory capacity, medium-term memory preserves important user context from earlier in the same conversation through recursive summarization.

## **2. Memory Architecture**

### **2.1 Three-Tier Memory System Context**

- **Short-term Memory**: Last 10 messages (immediate context)
- **Medium-term Memory**: User-focused summary from earlier in current conversation
- **Long-term Memory**: Persistent user profile across sessions (separate system)

```
Complete Memory Architecture:

Intra-Conversational (Single Session):
├── Short-term Memory (last 10 messages in current conversation)
├── Medium-term Memory (user-focused summary of earlier conversation content)
└── Current Session Context (short-term + medium-term)

Cross-Conversational (Multiple Sessions):
├── Cross-Conversational Summary (unified summary from last 5 conversations)
│   ├── Combines short-term + medium-term from each conversation
│   └── Provides context for new sessions
└── Long-term Memory (persistent user profile - separate system)
```

Medium-term memory bridges short-term immediate context with long-term persistent memory, ensuring conversational continuity within sessions.

## **3. Medium-Term Memory Generation**

### **3.1 Recursive Summary Approach**

**Trigger**: When conversation exceeds short-term memory capacity (more than 10 messages)

**Implementation: Simple Recursive Integration**
- When message count reaches 11: Create initial medium-term summary from messages 1-10 (user-focused)
- Every 10 messages after (21, 31, 41...): Update summary by integrating previous summary + new user content from messages that have completely moved out of short-term window
- Always keep last 10 messages as short-term memory
- Single evolving summary that grows and consolidates over time

**Recursive Update Process:**
1. **Previous Summary Integration**: Take existing medium-term summary as foundation
2. **New Content Analysis**: Extract user insights from new messages beyond short-term window
3. **Synthesis**: Combine previous summary with new user content, consolidating patterns
4. **Evolution**: Update summary to reflect user's journey and emerging themes
5. **Compression**: Keep within token limits while preserving essential user information

**Evolving Medium-Term Summary Structure:**
```markdown
# Medium-Term Memory

## User's Journey & Insights
- Important realizations and patterns user has discovered
- Emotional shifts and growth moments
- Connections they've made between different aspects of their experience

## Current Situation & Context
- What's happening in user's life right now
- Active challenges and circumstances
- Immediate context and concerns

## Ongoing Work & Interests
- Practices, approaches, and areas user is exploring
- Therapeutic or spiritual work in progress
- Topics they want to continue developing

## Preferences & Patterns
- How user likes to receive guidance and support
- Communication style and approach preferences
- Recurring themes and ongoing concerns

---
*Updated: [timestamp] | Version: [number]*
```

**Token Management:**
- **Target Range**: 500-1000 tokens per update
- **Growth Limit**: Maximum 7000 tokens total
- **Compression**: When approaching limit, consolidate and compress while preserving key insights

### **3.2 Recursive Update Quality Criteria**

**Integration Quality**: Successfully merge previous summary with new user content
**Pattern Recognition**: Identify and consolidate recurring themes and insights
**Evolution Tracking**: Capture user's journey and growth throughout conversation
**User Focus**: Prioritize user insights over agent responses (since agent writes most text)
**Therapeutic Continuity**: Maintain coherent narrative of user's spiritual/emotional work

### **3.3 Recursive Integration Prompts**

**Initial Summary Creation (Message 11):**
```
Create an initial medium-term memory summary focusing on USER content and insights from the conversation so far.

Since the agent generates most text, extract and preserve:
1. User's insights, breakthroughs, and realizations
2. User's emotional journey and current state
3. Important personal context and situation
4. User's spiritual/therapeutic work and preferences
5. User's ongoing concerns and questions

Messages to analyze (1-10): [MESSAGES]

Format as structured markdown with sections: Key Insights & Breakthroughs, Current Situation, Ongoing Work & Interests, Preferences & Patterns.
Target: 500-1000 tokens.
```

**Recursive Update (Every 10 messages):**
```
Update the existing medium-term memory by integrating new user content with the previous summary.

Previous Summary:
[EXISTING_SUMMARY]

New User Content (messages [X] to [Y]):
[NEW_MESSAGES]

Create an evolved summary that:
1. Integrates new insights with previous understanding
2. Consolidates patterns and recurring themes
3. Updates user's journey and emotional evolution
4. Maintains focus on user content (not agent responses)
5. Preserves essential context while staying concise

Keep the same structure but evolve the content. Target: 500-1000 tokens.
```

## **4. Context Assembly for Agent**

### **4.1 Intra-Conversational Context Assembly**

**When**: Each user message during an ongoing conversation

**Process**:
1. **Short-term Memory**: Last 10 messages (immediate context)
2. **Medium-term Memory**: Single user-focused summary from earlier in conversation
3. **Full Context Assembly**: Combine medium-term summary + short-term messages for agent
4. **Context Injection**: Provide complete intra-conversational context to agent

### **4.2 Context Structure for Agent**

```markdown
# Current Conversation Context

## Medium-Term Memory (User Context from Earlier)
[Single comprehensive summary focusing on user's insights, emotional states, 
personal information, spiritual work, preferences, and ongoing concerns 
from earlier in this conversation]

## Short-Term Memory (Recent Messages)
- Message 26: [User message]
- Message 27: [Assistant response]
- Message 28: [User message]
- [... last 10 messages]

## Current Message
- Message 35: [Current user input requiring response]
```

### **5.2 Session Data Format**

**Session Markdown Structure:**
```markdown
# Session: 2024-01-15_143022

## Metadata
- Start: 2024-01-15T14:30:22Z
- End: 2024-01-15T15:45:18Z  
- Message Count: 28
- Summary Version: 3

## Short-Term Messages (Last 10)
**Message 19 (User):** I've been thinking about what we discussed...
**Message 20 (Assistant):** That's wonderful that you're reflecting...
[... last 10 messages]

## Medium-Term Summary
[User-focused summary content]
```

### **5.3 Corrected Example Flow**

**Messages 1-10**: All in short-term memory
**Message 11**: 
- Create medium-term summary from messages 1-10
- Short-term memory = messages 2-11 (last 10)

**Messages 12-20**: No updates, short-term = messages 11-20

**Message 21**: 
- Update medium-term summary by integrating messages 2-11 (completely moved out of short-term)
- Short-term memory = messages 12-21 (last 10)

**Messages 22-30**: No updates, short-term = messages 21-30

**Message 31**:
- Update medium-term summary by integrating messages 12-21 (completely moved out of short-term)
- Short-term memory = messages 22-31 (last 10)

*Clean separation - no duplication between medium-term and short-term memory*

**Growth and Compression Strategy:**
- **Initial**: 500-1000 tokens (message 11)
- **Growth**: Evolves with each update, may grow to 7000 tokens maximum
- **Compression**: When approaching 7000 tokens, consolidate and compress while preserving essential user insights and patterns

### **5.4 Session Memory Management**

**Update Frequency**: Recursive summary updates every 10 messages after initial creation (message 11)
**Retention**: Single evolving summary maintained throughout session
**Session Completion**: Save final summary with session data when conversation ends
**Cleanup**: Archive completed sessions after 30 days (user configurable)
**Growth Management**: Compress summary when approaching 7000 token limit

---

*This document serves as the comprehensive design specification for the medium-term memory system, focusing on intra-conversational continuity and context preservation.* 