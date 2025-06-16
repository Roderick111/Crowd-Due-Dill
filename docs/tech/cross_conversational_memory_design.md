# **Cross-Conversational Memory Design**

## **1. Overview**

Cross-conversational memory provides unified context from multiple past conversations for new sessions. This system combines medium-term and short-term memory from the last 5 conversations to create a comprehensive summary that helps maintain continuity across separate sessions.

## **2. Memory Architecture Context**

### **2.1 Integration with Other Memory Systems**

- **Short-term Memory**: Last 10 messages (immediate context within session)
- **Medium-term Memory**: User-focused summary from earlier in current conversation
- **Cross-conversational Memory**: Unified summary from multiple past sessions
- **Long-term Memory**: Persistent user profile across sessions (separate system)

Cross-conversational memory bridges individual session contexts with persistent long-term memory, providing continuity between separate conversations.

## **3. Cross-Conversational Summary Generation**

### **3.1 Summary Creation Process**

**Purpose**: Provide unified context from multiple past conversations for new sessions

**Trigger**: When user starts a new conversation

**Process**:
1. **Gather Last 5 Conversations**: Collect both short-term and medium-term memory from each
2. **Unified Summarization**: Create comprehensive summary combining all contexts
3. **Context Injection**: Provide cross-conversational summary to agent for new session context

### **3.2 Cross-Conversational Summary Structure**

**Token Budget**: 500-1000 tokens total

```markdown
# Cross-Conversational Context

## Recent Highlights
- Key insights and breakthroughs from last conversation
- Current emotional state and immediate concerns
- Active spiritual/therapeutic work in progress

## Patterns Across Sessions
- Recurring themes and ongoing challenges
- Consistent interests and preferred approaches
- Evolution in user's journey and growth areas

## Current Context
- Where user is now in their process
- What they're actively working on
- How they prefer to receive guidance

---
*Summary of last 5 conversations | Updated: [timestamp]*
```

### **3.3 Cross-Conversational Integration Algorithm**

```python
def generate_cross_conversational_summary(user_id):
    # Get last 5 conversations
    recent_conversations = get_recent_conversations(user_id, limit=5)
    
    contexts = []
    for conv in recent_conversations:
        # Combine short-term and medium-term from each conversation
        context = {
            'short_term': conv.get('short_term_messages', []),
            'medium_term': conv.get('medium_term_summary', ''),
            'date': conv.get('date'),
            'session_id': conv.get('session_id')
        }
        contexts.append(context)
    
    # Generate unified summary
    unified_summary = create_unified_summary(contexts)
    
    return unified_summary

def create_unified_summary(conversation_contexts):
    """Create unified summary from multiple conversation contexts"""
    prompt = f"""
    Create a unified cross-conversational summary (500-1000 tokens) from the following conversation contexts.
    Focus on:
    1. Recent session highlights from the most recent conversation
    2. Recurring themes and patterns across all sessions
    3. User's current context and ongoing work
    
    Conversation contexts:
    {format_contexts_for_summarization(conversation_contexts)}
    
    Format as structured markdown with Recent Highlights, Patterns Across Sessions, and Current Context sections.
    """
    
    return llm.invoke(prompt)
```

## **4. Context Assembly for New Sessions**

### **4.1 Cross-Conversational Context Assembly**

**When**: User starts a new conversation

**Process**:
1. **Cross-Conversational Summary**: Generate unified summary from last 5 conversations
2. **Context Injection**: Provide cross-conversational context to agent for new session
3. **Fresh Session Start**: Begin new short-term and medium-term memory for current conversation

### **4.2 New Session Context Structure**

```markdown
# New Conversation Context

## Cross-Conversational Context
[Unified summary from last 5 conversations combining their short-term 
and medium-term memory, providing recent highlights, recurring themes, 
and current user context]

## Current Session
- Short-term Memory: [Empty - new conversation]
- Medium-term Memory: [Empty - will build as conversation progresses]
```

## **5. Storage and File Management**

### **5.1 File Structure**

```
data/
├── users/
│   ├── user_123/
│   │   ├── sessions/
│   │   │   ├── 2024-01-15_143022.md
│   │   │   ├── 2024-01-18_091245.md
│   │   │   └── 2024-01-22_160830.md
│   │   └── cross_conversational_summary.md
│   └── user_456/
│       ├── sessions/
│       │   └── ...
│       └── cross_conversational_summary.md
```

### **5.2 Cross-Conversational Summary Format**

```markdown
# Cross-Conversational Context

## Recent Highlights
- User had breakthrough recognizing inner critic as protector part
- Working on relationship anxiety and boundary setting
- Planning new moon ritual, established daily meditation practice
- Interested in IFS parts work approach

## Patterns Across Sessions
- Recurring focus on spiritual practices and lunar timing
- Ongoing work with relationship dynamics and boundaries
- Preference for gentle, collaborative guidance approaches
- Evolution from anxiety toward more grounded exploration

## Current Context
- Generally more grounded, working through relationship dynamics
- Active daily meditation practice and lunar awareness
- Immediate focus on boundary work and spiritual practice integration
- Seeks gentle guidance on relationships and spiritual development

---
*Summary of last 5 conversations | Updated: 2024-01-22T16:30:00Z*
```

### **5.3 Update and Maintenance**

**Update Frequency**: Generated fresh for each new conversation
**Source Data**: Last 5 completed conversations (short-term + medium-term memory)
**Token Management**: Target 500-1000 tokens total
**Retention**: Overwrites previous cross-conversational summary with each update
**Cleanup**: Automatically maintained as part of new session initialization

---

*This document serves as the comprehensive design specification for the cross-conversational memory system, focusing on continuity between separate sessions.* 