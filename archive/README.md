# Archive Directory

This directory contains **LEGACY/UNUSED** files that are no longer part of the active codebase.

## ⚠️ **IMPORTANT WARNING**
**These files are NOT used by the current application and are kept only for historical reference.**

## 📁 Directory Structure

### `legacy-utils/` 
Contains utility modules that were developed but are no longer integrated into the main application:

- **`relevance_evaluator.py`** - Standalone relevance evaluation system for RAG quality assessment
  - Status: **UNUSED** - Not integrated into current RAG pipeline
  - Purpose: Was designed to evaluate retrieval quality using LLM-based scoring
  - Reason for archival: Redundant functionality, performance overhead

- **`semantic_domain_detector.py`** - Semantic domain detection using OpenAI embeddings  
  - Status: **UNUSED** - Not integrated into current domain system
  - Purpose: Was designed to auto-detect query domains using cosine similarity
  - Reason for archival: Current domain system is manual activation based

## 🚫 **Do Not Use These Files**

These files are kept for:
- Historical reference
- Code examples
- Potential future inspiration
- Documentation of attempted approaches

## 🔄 **If You Need Similar Functionality**

Instead of using these legacy files:
1. Check the current `src/` directory for active implementations
2. Refer to the main application documentation
3. Consider if the functionality is actually needed
4. Implement fresh solutions following current architecture patterns

---
*Last updated: June 15, 2025*
*Archived during production deployment cleanup* 