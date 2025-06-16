#!/usr/bin/env python3
"""
Negative Intent Detection for Q&A Cache System
Prevents inappropriate responses to negative queries
"""

from typing import List, Set


class NegativeIntentDetector:
    """Detects negative intent in user queries to prevent inappropriate responses"""
    
    # Critical negation words that ALWAYS indicate negative intent
    CRITICAL_NEGATION_WORDS: Set[str] = {
        'not', 'never', "don't", "can't", "shouldn't", "won't", "isn't", "aren't",
        'dont', 'cant', 'shouldnt', 'wont', 'isnt', 'arent', 'no', 'none'
    }
    
    # Strong negative intent words
    STRONG_NEGATIVE_WORDS: Set[str] = {
        'avoid', 'dangerous', 'harmful', 'stop', 'fail', 'bad', 'wrong',
        'against', 'dispose', 'get rid', 'remove', 'toxic', 'unsafe', 'risky',
        'refuse', 'reject', 'oppose', 'prevent', 'block', 'forbidden'
    }
    
    # Contextual negative words (require more context)
    CONTEXTUAL_NEGATIVE_WORDS: Set[str] = {
        'problem', 'issue', 'concern', 'warning', 'caution'
    }
    
    # Negative phrases (more context-sensitive)
    NEGATIVE_PHRASES: Set[str] = {
        'why should i avoid', 'is it dangerous', 'why not to', 'problems with',
        'issues with', 'side effects', 'negative effects', 'what not to',
        'when not to', 'how to stop', 'how to avoid', 'why avoid',
        'instead of', 'rather than', 'opposite of'
    }
    
    def __init__(self, sensitivity: float = 0.85):
        """
        Initialize negative intent detector
        
        Args:
            sensitivity: Threshold for contextual negative detection (0.0-1.0)
        """
        self.sensitivity = sensitivity
    
    def has_negative_intent(self, query: str) -> bool:
        """
        Check if query contains negative intent
        
        Args:
            query: User query to analyze
            
        Returns:
            True if negative intent detected, False otherwise
        """
        if not query or not query.strip():
            return False
        
        query_lower = query.lower().strip()
        
        # Step 1: Check for negative phrases first (most specific)
        if self._contains_negative_phrases(query_lower):
            return True
        
        # Step 2: Check for critical negation words (ALWAYS negative intent)
        if self._contains_critical_negation(query_lower):
            return True
        
        # Step 3: Check for strong negative words
        if self._contains_strong_negative_words(query_lower):
            return True
        
        # Step 4: Check for contextual negative words (with threshold)
        if self._contains_contextual_negative_words(query_lower):
            return True
        
        return False
    
    def _extract_clean_words(self, query_lower: str) -> set:
        """Extract clean words from query, removing punctuation"""
        import re
        # Remove punctuation and split into words
        clean_text = re.sub(r'[^\w\s]', ' ', query_lower)
        return set(clean_text.split())
    
    def _contains_negative_phrases(self, query_lower: str) -> bool:
        """Check for specific negative phrases"""
        return any(phrase in query_lower for phrase in self.NEGATIVE_PHRASES)
    
    def _contains_critical_negation(self, query_lower: str) -> bool:
        """Check for critical negation words that ALWAYS indicate negative intent"""
        words_in_query = self._extract_clean_words(query_lower)
        critical_matches = words_in_query.intersection(self.CRITICAL_NEGATION_WORDS)
        
        if not critical_matches:
            return False
        
        # Special handling for "no" - only negative if it's not part of a compound word
        if 'no' in critical_matches and len(critical_matches) == 1:
            # Check if "no" is standalone or part of another word
            words_list = query_lower.split()
            for word in words_list:
                if word == 'no':  # Standalone "no"
                    return True
                elif 'no' in word and len(word) > 2:  # Part of another word like "know"
                    continue
            return False
        
        # Any other critical negation word is always negative intent
        return True
    
    def _contains_strong_negative_words(self, query_lower: str) -> bool:
        """Check for strong negative words"""
        words_in_query = self._extract_clean_words(query_lower)
        strong_matches = words_in_query.intersection(self.STRONG_NEGATIVE_WORDS)
        
        if not strong_matches:
            return False
        
        # If query is short and contains strong negative words, likely negative intent
        if len(words_in_query) <= 5:
            return True
        
        # If multiple strong negative words, likely negative intent
        if len(strong_matches) >= 2:
            return True
        
        # Single strong negative word in longer query - use threshold
        negative_ratio = len(strong_matches) / len(words_in_query)
        return negative_ratio >= (1.0 - self.sensitivity)
    
    def _contains_contextual_negative_words(self, query_lower: str) -> bool:
        """Check for contextual negative words with higher threshold"""
        words_in_query = self._extract_clean_words(query_lower)
        contextual_matches = words_in_query.intersection(self.CONTEXTUAL_NEGATIVE_WORDS)
        
        if not contextual_matches:
            return False
        
        # Contextual words need higher confidence
        if len(words_in_query) <= 3:  # Very short queries
            return True
        
        # Multiple contextual negative words
        if len(contextual_matches) >= 2:
            return True
        
        # Single contextual word needs high ratio
        negative_ratio = len(contextual_matches) / len(words_in_query)
        return negative_ratio >= 0.3  # 30% threshold for contextual words
    
    def get_negative_indicators(self, query: str) -> List[str]:
        """
        Get list of negative indicators found in query (for debugging)
        
        Args:
            query: User query to analyze
            
        Returns:
            List of negative words/phrases found with their categories
        """
        if not query:
            return []
        
        query_lower = query.lower().strip()
        indicators = []
        
        # Find negative phrases
        for phrase in self.NEGATIVE_PHRASES:
            if phrase in query_lower:
                indicators.append(f"phrase: '{phrase}'")
        
        # Find critical negation words
        words_in_query = self._extract_clean_words(query_lower)
        critical_words = words_in_query.intersection(self.CRITICAL_NEGATION_WORDS)
        for word in critical_words:
            indicators.append(f"critical: '{word}'")
        
        # Find strong negative words
        strong_words = words_in_query.intersection(self.STRONG_NEGATIVE_WORDS)
        for word in strong_words:
            indicators.append(f"strong: '{word}'")
        
        # Find contextual negative words
        contextual_words = words_in_query.intersection(self.CONTEXTUAL_NEGATIVE_WORDS)
        for word in contextual_words:
            indicators.append(f"contextual: '{word}'")
        
        return indicators
    
    def get_stats(self) -> dict:
        """Get statistics about the negative intent detector"""
        return {
            'critical_negation_words': len(self.CRITICAL_NEGATION_WORDS),
            'strong_negative_words': len(self.STRONG_NEGATIVE_WORDS),
            'contextual_negative_words': len(self.CONTEXTUAL_NEGATIVE_WORDS),
            'negative_phrases_count': len(self.NEGATIVE_PHRASES),
            'sensitivity': self.sensitivity
        } 