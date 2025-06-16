# **Esoteric Vectors Memory System Design**

## **1. Overview**

The Esoteric Vectors memory system implements a three-tier architecture designed to provide therapeutic continuity and personalized spiritual guidance across conversations. The system balances technical simplicity with therapeutic effectiveness, focusing on user privacy and transparent memory management.

## **2. Memory Architecture**

### **2.1 Three-Tier Memory Structure**

```
Memory Hierarchy:
├── Short-term Memory (10 last messages)
├── Medium-term Memory (conversation summaries)
└── Long-term Memory (user profile with key insights)
```

**Short-term Memory:**
- Direct access to last 10 messages in current conversation
- Provides immediate conversational context
- No processing required - raw message history

**Medium-term Memory:**
- Summarized content from previous conversations
- Bridges gap between current session and long-term insights
- Generated through conversation summarization after each session

**Long-term Memory:**
- Curated user profile with most important insights
- Cross-conversational persistent memory
- Focus on therapeutic continuity and personalization

### **2.2 Short-Term and Medium-Term Memory**

**Short-Term Memory**: Last 10 messages in current conversation (immediate context)

**Medium-Term Memory**: User-focused summary of earlier conversation content that has moved beyond the short-term window. Since the agent generates most text, this focuses specifically on user insights, emotional states, personal information, spiritual work, and preferences from earlier in the same conversation.

**Overlapping Window**: When conversation exceeds 15 messages, medium-term summary is created/updated from messages beyond the short-term window, with 5-message overlap to maintain continuity.

### **2.3 Cross-Conversational Memory Logic**

When a new conversation begins, the system provides context from previous sessions:

**Cross-Conversational Memory Assembly:**
1. **Summary Generation**: Create unified summary (500-1000 tokens) combining short-term and medium-term memory from last 5 conversations
2. **Long-term Memory Integration**: Inject persistent user profile (long-term memory) into agent context
3. **Complete Context Provision**: Provide agent with cross-conversational summary + long-term profile for informed responses

**New Conversation Context Structure:**
```
New Conversation Context:
├── Cross-Conversational Summary (200-400 tokens)
│   ├── Recent session highlights from last conversation
│   ├── Recurring themes across last 5 sessions
│   └── Current user context and ongoing work
├── Long-term Memory Profile (1000 tokens)
│   ├── Personal preferences
│   ├── Spiritual work patterns
│   └── Emotional patterns and breakthroughs
└── Current Session Context (empty at start)
    ├── Short-term memory (will populate with new messages)
    └── Medium-term memory (will build as conversation progresses)
```

This approach ensures each new conversation benefits from both recent session context and persistent user insights while maintaining manageable context size.

## **3. Long-Term Memory System**

### **3.1 Profile Structure**

**Token Budget: 1000 tokens maximum**

```
User Profile Categories:
├── Personal Preferences (200-300 tokens)
│   ├── Communication style preferences
│   ├── Guidance approach preferences
│   └── General spiritual preferences
├── Spiritual Work (200-300 tokens)
│   ├── Current esoteric focus areas (lunar work, crystal healing, etc.)
│   ├── Spiritual practice preferences and evolution
│   ├── Esoteric goals and intentions
│   └── Practice development and affinity patterns
└── Emotional Patterns (400-500 tokens)
    ├── Psychological frameworks (IFS, Jungian, attachment - if used)
    ├── Core emotional themes and breakthrough moments
    ├── Recurring patterns, triggers, and coping strategies
    ├── Progress tracking and growth areas
    └── Observed correlations (non-causal patterns)
```

**Category Priorities:**
- **Emotional Patterns**: Highest importance for therapeutic continuity
- **Spiritual Work**: Medium importance for guidance personalization
- **Personal Preferences**: Lower importance but essential for communication style

### **3.2 Insight Extraction Process**

**Real-time Flagging:**
- Scan each user message for potential insights
- Flag messages containing:
  - Emotional revelations or breakthroughs
  - Spiritual practice updates or changes
  - Personal preference expressions
  - Recurring pattern mentions
  - Therapeutic progress indicators

**Batch Processing (Every 5 Messages):**
- Process all flagged messages from last 5 messages
- Extract insights with importance scoring (0.4-1.0)
- Store insights normally in the user profile
- Include very concise conversational context for better extraction quality

**Importance Scoring Criteria:**
```
High Importance (0.8-1.0):
├── Breakthrough moments
├── Trauma revelations or healing
├── Major spiritual insights
└── Significant behavioral pattern recognition

Medium Importance (0.5-0.7):
├── Preference clarifications
├── Practice updates
├── Emotional pattern confirmations
└── Communication style feedback

Low Importance (0.2-0.4):
├── Casual preferences
├── Minor practice adjustments
└── General spiritual interests
```

### **3.3 Profile Update and Merge Process**

**Update Trigger: Every 20 Messages (Cross-Conversational)**
- Message count continues across conversation boundaries
- Ensures regular profile maintenance without over-processing

**Merge Algorithm:**
1. **Categorization**: Sort new insights into appropriate profile categories
2. **Similarity Detection**: Identify related insights within categories
3. **Consolidation**: Merge similar insights with enhanced context
4. **Evolution Tracking**: Update existing insights with new information
5. **Confidence Updating**: Adjust confidence levels based on confirmation/contradiction
6. **Compression**: Ensure profile stays within 1000 token limit

**Consolidation Examples:**
```
Individual Insights:
- "User felt anxious during yesterday's new moon"
- "User mentioned new moon sensitivity last month"
- "User experiences restlessness during lunar transitions"

Consolidated Pattern:
- "User consistently experiences anxiety and restlessness during new moon phases (confirmed multiple times, high confidence)"
```

**Evolution Tracking:**
```
Profile Evolution:
├── Original: "User struggling with daily meditation"
├── Update: "User established morning meditation routine"
├── Latest: "User maintains consistent 20-minute daily meditation practice"
```

### **3.4 Confidence and Importance Management**

**Confidence Scoring (0.0-1.0):**
- **Initial**: New insights start at 0.7 confidence
- **Confirmation**: Increases to 0.9 when pattern repeats
- **User Validation**: Reaches 1.0 when user explicitly confirms
- **Time Decay**: Decreases by 0.1 every 30 days
- **Contradiction**: Drops to 0.3 when conflicting insight emerges

**Importance Evolution:**
- **Breakthrough Moments**: Maintain high importance over time
- **Preferences**: May decrease in importance as they become established
- **Patterns**: Increase in importance as they're confirmed repeatedly
- **Outdated Information**: Automatically flagged for review/removal

### **3.5 Profile Compression Strategy**

**When profile exceeds 1000 tokens:**

1. **Priority Preservation**: Never compress breakthrough moments or core emotional patterns
2. **Preference Consolidation**: Merge similar preferences into broader statements
3. **Pattern Summarization**: Convert multiple examples into general patterns
4. **Historical Archiving**: Move oldest, lowest-confidence insights to archive
5. **User Notification**: Inform user when significant compression occurs

**Compression Hierarchy:**
```
Compression Priority (Last to First):
├── Core Identity Elements (never compress)
├── Recent Breakthrough Moments (preserve detail)
├── Confirmed Emotional Patterns (summarize examples)
├── Spiritual Work Progress (consolidate updates)
└── General Preferences (merge similar items)
```

## **4. User Agency and Transparency**

### **4.1 User Controls**

**Profile Access:**
- **"What do you remember about me?"**: Display current profile in readable format
- **Profile categories**: Show insights organized by category
- **Confidence indicators**: Display confidence levels for major insights
- **Source tracking**: Show which conversations contributed to insights

**Memory Management:**
- **"Forget that I mentioned X"**: Remove specific insights or categories
- **"Update: I no longer feel Y"**: Direct profile corrections
- **"That's not quite right"**: Flag inaccurate insights for review
- **"Clear all memories"**: Complete profile reset option

**Transparency Features:**
- **Change Log**: Track profile updates with timestamps
- **Insight Sources**: Link insights back to originating conversations
- **Confidence Levels**: Show how certain the system is about each insight
- **Processing Status**: Indicate when profile updates occur

### **4.2 Privacy and Security**

**Storage Architecture:**
- **Local Storage**: Encrypted JSON files in user's data directory
- **User-Controlled Encryption**: User manages encryption keys
- **No Cloud Dependency**: Complete local operation for privacy
- **Data Portability**: Easy export/import of user profiles

**Privacy Controls:**
- **Granular Deletion**: Remove specific insights, categories, or time periods
- **Processing Transparency**: Clear indication of what's being remembered
- **Opt-out Options**: Disable memory features entirely if desired
- **Data Retention**: Automatic cleanup of low-confidence, old insights

## **5. Technical Implementation**

### **5.1 Storage Structure**

**Markdown File-Based Storage:**
User profiles are stored as human-readable Markdown files, providing transparency, simplicity, and user control.

```
data/
├── user_profiles/
│   ├── user_123.md
│   ├── user_456.md
│   └── ...
├── conversation_summaries/
│   ├── user_123_conversations.md
│   └── ...
└── profile_backups/
    └── automated_backups/
```

**Profile File Structure (user_123.md):**
```markdown
# User Profile: [User ID]

**Created:** 2024-01-15  
**Last Updated:** 2024-02-20  
**Message Count:** 45  
**Total Tokens:** ~850

## Personal Preferences
- Prefers gentle, intuitive guidance over direct instruction
- Responds well to metaphorical explanations
- Communication style: Warm and supportive approach
- Dislikes overly analytical responses

## Spiritual Work
- **Current Focus:** Lunar work and crystal healing practices
- **Daily Practice:** 20-minute morning meditation with amethyst (established routine)
- **Esoteric Preferences:** Prefers working with moon phases, drawn to water element practices
- **Practice Evolution:** Started with basic meditation, now incorporating lunar timing
- **Goals:** Developing deeper connection to natural cycles and energy work
- **Crystal Affinity:** Resonates with amethyst and rose quartz for emotional balance

## Emotional Patterns
### Psychological Framework (if applicable)
- **IFS Parts Work**: Inner critic (recognized as protector), perfectionist part
- **Jungian Elements**: Working with shadow aspects, anima integration
- **Attachment Patterns**: Fear of abandonment, developing secure self-attachment

### Core Emotional Themes
- **Breakthrough Moment (2024-01-15):** Recognized inner critic as protective part, leading to self-compassion practice
- **Recurring Themes**: Fear of abandonment in relationships, triggers during conflict
- **Triggers**: Criticism from authority figures, feeling misunderstood
- **Coping Strategies**: IFS techniques, meditation, shadow work practices

### Progress and Growth
- **Emotional Regulation**: Improved awareness, using therapeutic techniques for self-soothing
- **Growth Areas**: Conflict resolution, boundary setting, self-compassion development
- **Observed Correlations**: Notices increased anxiety during new moon phases (pattern noted, not causal)

---
*Profile managed by Esoteric Vectors Memory System*
```

**Metadata Tracking:**
```python
# Profile metadata stored in file header
profile_metadata = {
    "user_id": "extracted_from_filename",
    "created": "parsed_from_markdown",
    "last_updated": "parsed_from_markdown", 
    "message_count": "parsed_from_markdown",
    "estimated_tokens": "calculated_from_content"
}
```

### **5.2 Integration with Existing Architecture**

**File-Based Storage Integration:**
- **User Profiles**: Markdown files in `data/user_profiles/`
- **Conversation Summaries**: Markdown files in `data/conversation_summaries/`
- **No Vector Database**: Direct file I/O for profile management
- **Domain Integration**: Memory insights can reference relevant domains in markdown

**Agent Context Injection:**
```python
# Context Assembly for Each Query
def assemble_context(user_id, current_messages):
    # Load user profile from markdown file
    profile_content = load_user_profile(f"data/user_profiles/{user_id}.md")
    
    # Load conversation summaries
    conversation_summary = load_conversation_summary(f"data/conversation_summaries/{user_id}_conversations.md")
    
    # Assemble complete context
    agent_context = {
        "system_prompt": "...",
        "short_term_memory": current_messages[-10:],
        "cross_conversational_summary": conversation_summary,
        "long_term_memory": profile_content,  # Full markdown profile
        "domain_context": relevant_domain_knowledge
    }
    return agent_context
```

**Profile Management:**
```python
class UserProfileManager:
    def load_profile(self, user_id):
        """Load user profile from markdown file"""
        file_path = f"data/user_profiles/{user_id}.md"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self.create_empty_profile(user_id)
    
    def update_profile(self, user_id, new_insights):
        """Parse markdown, merge insights, write back to file"""
        current_profile = self.load_profile(user_id)
        updated_profile = self.merge_insights(current_profile, new_insights)
        self.save_profile(user_id, updated_profile)
        self.backup_profile(user_id)
    
    def backup_profile(self, user_id):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/profile_backups/{user_id}_{timestamp}.md"
        shutil.copy(f"data/user_profiles/{user_id}.md", backup_path)
```

### **5.3 Processing Pipeline**

**Message Processing Flow:**
1. **Real-time Flagging**: Scan incoming message for insight potential
2. **Batch Extraction**: Process flagged messages every 5 messages
3. **Profile Update**: Merge insights into markdown profile every 20 messages
4. **File Management**: Parse and update markdown structure, maintain formatting
5. **Backup Creation**: Automatic timestamped backups before major updates
6. **Token Estimation**: Calculate profile size and compress if needed
7. **User Notification**: Inform user of significant profile changes

**Markdown Processing:**
```python
def update_markdown_profile(user_id, new_insights):
    # Load current profile
    profile_content = load_profile(user_id)
    
    # Parse markdown structure
    sections = parse_markdown_sections(profile_content)
    
    # Merge new insights into appropriate sections
    updated_sections = merge_insights_into_sections(sections, new_insights)
    
    # Regenerate markdown with proper formatting
    updated_profile = generate_markdown_profile(updated_sections)
    
    # Save updated profile
    save_profile(user_id, updated_profile)
    
    # Create backup
    backup_profile(user_id)
```

## **6. Quality Control and Validation**

### **6.1 Insight Quality Filters**

**Importance Threshold**: Only store insights with importance ≥ 0.4
**Specificity Filter**: Reject vague insights ("User feels good")
**Actionability Check**: Ensure insights can improve future conversations
**Context Validation**: Verify insights make sense within conversation context
**Framework Flexibility**: Adapt emotional pattern structure based on user's preferred psychological approaches (IFS, Jungian, purely esoteric, etc.)

### **6.2 Error Handling and Recovery**

**Contradiction Detection**: Flag conflicting insights for user review
**Confidence Decay**: Automatically reduce confidence of unconfirmed insights (30-day cycle)
**User Correction**: Allow users to correct or remove inaccurate memories
**Source Tracking**: Link each insight back to originating conversation for validation
**Memory Validation Prompts**: Periodic user confirmation of key insights ("I remember you mentioning X - is that still accurate?")
**Graceful Degradation**: System functions normally even with minimal memory

## **7. Success Metrics and Monitoring**

### **7.1 System Performance Metrics**

- **Profile Accuracy**: User correction rate as quality indicator
- **Therapeutic Value**: User retention and satisfaction with memory features
- **Processing Efficiency**: Cost and latency of memory operations
- **Storage Optimization**: Profile compression effectiveness

### **7.2 User Experience Metrics**

- **Memory Utilization**: How often stored insights enhance conversations
- **User Control Usage**: Frequency of memory management actions
- **Trust Indicators**: User willingness to share sensitive information
- **Personalization Effectiveness**: Improvement in conversation quality over time

## **8. Future Evolution**

### **8.1 Planned Enhancements**

**Temporal Awareness**: Track patterns related to lunar cycles, seasons, anniversaries
**Proactive Insights**: Surface relevant memories without explicit user queries
**Cross-User Learning**: Identify common patterns while preserving individual privacy
**Advanced Compression**: More sophisticated profile summarization techniques

### **8.2 Scalability Considerations**

**Local Processing**: Maintain privacy while enabling advanced features
**Efficient Storage**: Optimize profile storage and retrieval performance
**User Migration**: Support for transferring profiles between devices/installations
**Version Management**: Handle profile format evolution and backward compatibility

---

*This document serves as the comprehensive design specification for the Esoteric Vectors memory system, balancing therapeutic effectiveness with technical simplicity and user privacy.* 