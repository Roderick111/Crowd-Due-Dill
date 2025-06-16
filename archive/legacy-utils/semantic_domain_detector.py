#!/usr/bin/env python3
"""
⚠️  ARCHIVED/LEGACY FILE - DO NOT USE ⚠️

This file is UNUSED and archived for historical reference only.
It is NOT part of the current application and should NOT be imported or executed.

Archived on: June 15, 2025
Reason: Not integrated into current domain system (manual activation based)

Original Purpose:
Semantic Domain Detector - Uses OpenAI embeddings and cosine similarity to detect 
which knowledge domain a user query relates to. Was designed for intelligent 
domain activation hints.

For current domain functionality, see the active files in src/ directory.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
import numpy as np
from functools import lru_cache

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

class SemanticDomainDetector:
    """
    Detects knowledge domains using semantic similarity with pre-computed embeddings.
    
    Uses OpenAI embeddings and cosine similarity following Context7 best practices
    for reliable semantic similarity detection in production systems.
    """
    
    # Domain representative phrases for semantic matching
    DOMAIN_PHRASES = {
        "lunar": [
            "moon phases and lunar cycles",
            "connecting with moon goddess energy", 
            "lunar rituals and moon magic",
            "full moon new moon energy",
            "moon calendar and cosmic timing"
        ],
        "numerology": [
            "numerology and number meanings",
            "life path numbers and destiny numbers",
            "angel numbers and sacred numerology",
            "pythagorean numerology system",
            "number vibrations and frequencies"
        ],
        "ifs": [
            "internal family systems therapy",
            "parts work and inner child healing",
            "psychological integration and self-leadership",
            "trauma therapy and emotional healing",
            "inner critic and self-compassion"
        ],
        "astrology": [
            "astrology charts and birth charts",
            "zodiac signs and astrological houses",
            "planetary transits and aspects",
            "horoscope and astrological guidance",
            "natal chart interpretation"
        ],
        "crystals": [
            "crystal healing and gemstone energy",
            "chakra crystals and meditation stones",
            "crystal properties and metaphysical healing",
            "gemstone therapy and energy cleansing",
            "crystal grids and stone medicine"
        ],
        "tarot": [
            "tarot reading and card interpretation",
            "major arcana and minor arcana meanings",
            "tarot spreads and divination",
            "oracle cards and spiritual guidance",
            "tarot symbolism and archetypal wisdom"
        ],
        "archetypes": [
            "jungian archetypes and collective unconscious",
            "archetypal patterns and shadow work",
            "mythological symbols and archetypal psychology",
            "personality archetypes and human patterns",
            "symbolic wisdom and archetypal guidance"
        ]
    }
    
    # Minimum similarity threshold for domain detection
    SIMILARITY_THRESHOLD = 0.3
    
    def __init__(self):
        """Initialize the semantic domain detector."""
        self.embeddings = None
        self.domain_embeddings = {}
        self._setup_embeddings()
        
    def _setup_embeddings(self):
        """Initialize OpenAI embeddings with error handling."""
        if OpenAIEmbeddings is None:
            print("⚠️  OpenAI embeddings not available - domain detection disabled")
            return
            
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                show_progress_bar=False
            )
            self._precompute_domain_embeddings()
            print("✅ Semantic domain detector ready")
        except Exception as e:
            print(f"⚠️  Failed to initialize domain detector: {e}")
            self.embeddings = None
    
    def _precompute_domain_embeddings(self):
        """Pre-compute embeddings for all domain phrases for efficiency."""
        if not self.embeddings:
            return
            
        try:
            for domain, phrases in self.DOMAIN_PHRASES.items():
                # Embed all phrases for this domain
                phrase_embeddings = self.embeddings.embed_documents(phrases)
                # Store as numpy arrays for efficient cosine similarity
                self.domain_embeddings[domain] = [
                    np.array(embedding) for embedding in phrase_embeddings
                ]
        except Exception as e:
            print(f"⚠️  Failed to precompute domain embeddings: {e}")
            self.domain_embeddings = {}

    @lru_cache(maxsize=256)
    def detect_query_domain(self, query: str) -> Optional[Tuple[str, float]]:
        """
        Detect which domain a query is most related to using semantic similarity.
        
        Args:
            query: User query text
            
        Returns:
            Tuple of (domain_name, similarity_score) or None if no strong match
        """
        if not self.embeddings or not self.domain_embeddings:
            return None
            
        try:
            # Embed the query
            query_embedding = np.array(self.embeddings.embed_query(query))
            
            # Find best matching domain
            best_domain = None
            best_similarity = 0.0
            
            for domain, phrase_embeddings in self.domain_embeddings.items():
                # Calculate maximum similarity with any phrase in this domain
                domain_similarities = [
                    self._cosine_similarity(query_embedding, phrase_embedding)
                    for phrase_embedding in phrase_embeddings
                ]
                max_similarity = max(domain_similarities)
                
                if max_similarity > best_similarity:
                    best_similarity = max_similarity
                    best_domain = domain
            
            # Return result only if above threshold
            if best_similarity >= self.SIMILARITY_THRESHOLD:
                return (best_domain, best_similarity)
            
            return None
            
        except Exception as e:
            print(f"⚠️  Domain detection error: {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Based on Context7 best practices for embedding similarity calculation.
        """
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
            
        return dot_product / (norm_vec1 * norm_vec2)
    
    def get_domain_suggestions(self, query: str, active_domains: List[str]) -> Dict[str, any]:
        """
        Get domain suggestions for activation hints.
        
        Args:
            query: User query
            active_domains: Currently active domains
            
        Returns:
            Dict with detection results and suggestions
        """
        detection_result = self.detect_query_domain(query)
        
        if not detection_result:
            return {
                "detected_domain": None,
                "similarity_score": 0.0,
                "needs_activation": False,
                "suggestion_message": None
            }
        
        detected_domain, similarity_score = detection_result
        needs_activation = detected_domain not in active_domains
        
        suggestion_message = None
        if needs_activation:
            domain_display_names = {
                "lunar": "Lunar Wisdom",
                "numerology": "Numerology", 
                "ifs": "Internal Family Systems Therapy",
                "astrology": "Astrology",
                "crystals": "Crystal Healing",
                "tarot": "Tarot & Divination",
                "archetypes": "Jungian Archetypes"
            }
            
            display_name = domain_display_names.get(detected_domain, detected_domain.title())
            suggestion_message = (
                f"💫 I sense you're asking about {display_name}. "
                f"To access specialized knowledge in this domain, "
                f"you can activate it with: 'domains enable {detected_domain}'"
            )
        
        return {
            "detected_domain": detected_domain,
            "similarity_score": similarity_score,
            "needs_activation": needs_activation,
            "suggestion_message": suggestion_message
        }
    
    def is_available(self) -> bool:
        """Check if domain detection is available."""
        return self.embeddings is not None and bool(self.domain_embeddings)
    
    def clear_cache(self):
        """Clear the LRU cache for query detection."""
        self.detect_query_domain.cache_clear()
    
    def get_stats(self) -> Dict[str, any]:
        """Get detector statistics."""
        cache_info = self.detect_query_domain.cache_info()
        return {
            "available": self.is_available(),
            "domains_loaded": len(self.domain_embeddings),
            "total_phrases": sum(len(phrases) for phrases in self.DOMAIN_PHRASES.values()),
            "cache_hits": cache_info.hits,
            "cache_misses": cache_info.misses,
            "cache_size": cache_info.currsize
        }