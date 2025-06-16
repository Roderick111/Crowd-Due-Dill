"""
⚠️  ARCHIVED/LEGACY FILE - DO NOT USE ⚠️

This file is UNUSED and archived for historical reference only.
It is NOT part of the current application and should NOT be imported or executed.

Archived on: June 15, 2025
Reason: Redundant functionality, not integrated into current RAG pipeline

For current functionality, see the active files in src/ directory.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI


class RelevanceEvaluator:
    """
    Standalone relevance evaluation system for assessing RAG retrieval quality.
    This is separate from the main RAG workflow and used only for optional assessment.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the relevance evaluator."""
        self.persist_directory = Path(persist_directory)
        self.relevance_log_file = self.persist_directory / "relevance_metrics.json"
        
        # Ensure directory exists
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize LLM for relevance evaluation
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=512  # Smaller token limit for evaluation
        )
        
        # Relevance evaluation prompt
        self.relevance_prompt = PromptTemplate(
            input_variables=["question", "retrieved_context"],
            template="""You are evaluating the relevance of retrieved information to a user's question.

User Question: {question}

Retrieved Context:
{retrieved_context}

Evaluate how relevant this retrieved context is to answering the user's question.

Provide a JSON response with:
- "score": a number from 0.0 to 1.0 (where 1.0 = highly relevant, 0.0 = not relevant)
- "reasoning": a brief explanation of your scoring

Format your response as valid JSON only, no additional text."""
        )
    
    def evaluate_relevance(self, question: str, retrieved_context: str) -> Dict[str, Any]:
        """
        Evaluate the relevance of retrieved context to a question.
        
        Args:
            question: The user's question
            retrieved_context: The retrieved context from RAG
            
        Returns:
            Dictionary with relevance score and details
        """
        try:
            # Create relevance evaluation prompt
            relevance_input = self.relevance_prompt.format(
                question=question,
                retrieved_context=retrieved_context[:2000]  # Limit context for efficiency
            )
            
            # Get relevance evaluation from LLM
            response = self.llm.invoke(relevance_input)
            
            # Parse JSON response
            parser = JsonOutputParser()
            relevance_result = parser.parse(response.content)
            
            relevance_score = float(relevance_result.get("score", 0.0))
            relevance_details = {
                "reasoning": relevance_result.get("reasoning", "No reasoning provided"),
                "context_length": len(retrieved_context),
                "timestamp": time.time(),
                "question_preview": question[:100] + "..." if len(question) > 100 else question
            }
            
            # Log the relevance score
            self._log_relevance_metric(question, relevance_score, relevance_details)
            
            return {
                "relevance_score": relevance_score,
                "relevance_details": relevance_details,
                "success": True
            }
            
        except Exception as e:
            print(f"⚠️ Relevance evaluation failed: {e}")
            return {
                "relevance_score": 0.5,  # Neutral score
                "relevance_details": {
                    "reasoning": f"Evaluation failed: {str(e)}",
                    "context_length": len(retrieved_context),
                    "timestamp": time.time(),
                    "question_preview": question[:100] + "..." if len(question) > 100 else question
                },
                "success": False,
                "error": str(e)
            }
    
    def _log_relevance_metric(self, question: str, score: float, details: Dict[str, Any]):
        """Log relevance metrics for performance monitoring."""
        try:
            # Load existing metrics
            metrics = []
            if self.relevance_log_file.exists():
                with open(self.relevance_log_file, 'r') as f:
                    metrics = json.load(f)
            
            # Add new metric
            metric_entry = {
                "question": question[:200],  # Truncate long questions
                "relevance_score": score,
                "details": details,
                "timestamp": time.time()
            }
            metrics.append(metric_entry)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(metrics) > 1000:
                metrics = metrics[-1000:]
            
            # Save updated metrics
            with open(self.relevance_log_file, 'w') as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to log relevance metric: {e}")
    
    def get_relevance_metrics(self, last_n: int = 50) -> Dict[str, Any]:
        """
        Get relevance monitoring metrics.
        
        Args:
            last_n: Number of recent queries to analyze
            
        Returns:
            Dictionary with relevance statistics
        """
        if not self.relevance_log_file.exists():
            return {
                "total_queries": 0,
                "recent_queries_analyzed": 0,
                "average_relevance": 0.0,
                "relevance_distribution": {
                    "high (≥0.7)": 0,
                    "medium (0.4-0.7)": 0,
                    "low (<0.4)": 0
                },
                "recent_queries": []
            }
        
        try:
            with open(self.relevance_log_file, 'r') as f:
                metrics = json.load(f)
            
            if not metrics:
                return {
                    "total_queries": 0,
                    "recent_queries_analyzed": 0,
                    "average_relevance": 0.0,
                    "relevance_distribution": {
                        "high (≥0.7)": 0,
                        "medium (0.4-0.7)": 0,
                        "low (<0.4)": 0
                    },
                    "recent_queries": []
                }
            
            # Get recent metrics
            recent_metrics = metrics[-last_n:] if len(metrics) > last_n else metrics
            
            # Calculate statistics
            scores = [m["relevance_score"] for m in recent_metrics]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            # Distribution counts
            high_count = sum(1 for s in scores if s >= 0.7)
            medium_count = sum(1 for s in scores if 0.4 <= s < 0.7)
            low_count = sum(1 for s in scores if s < 0.4)
            
            return {
                "total_queries": len(metrics),
                "recent_queries_analyzed": len(recent_metrics),
                "average_relevance": round(avg_score, 3),
                "relevance_distribution": {
                    "high (≥0.7)": high_count,
                    "medium (0.4-0.7)": medium_count,
                    "low (<0.4)": low_count
                },
                "recent_queries": [
                    {
                        "question": m["question"],
                        "score": m["relevance_score"],
                        "reasoning": m["details"].get("reasoning", "No reasoning"),
                        "timestamp": m["timestamp"]
                    }
                    for m in recent_metrics[-10:]  # Last 10 for preview
                ]
            }
            
        except Exception as e:
            print(f"❌ Error reading relevance metrics: {e}")
            return {
                "error": str(e),
                "total_queries": 0,
                "recent_queries_analyzed": 0,
                "average_relevance": 0.0,
                "relevance_distribution": {
                    "high (≥0.7)": 0,
                    "medium (0.4-0.7)": 0,
                    "low (<0.4)": 0
                },
                "recent_queries": []
            }
    
    def batch_evaluate_relevance(self, qa_pairs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Evaluate relevance for multiple question-context pairs.
        
        Args:
            qa_pairs: List of dicts with 'question' and 'context' keys
            
        Returns:
            List of relevance evaluation results
        """
        results = []
        
        for i, pair in enumerate(qa_pairs):
            print(f"📊 Evaluating relevance {i+1}/{len(qa_pairs)}...")
            
            result = self.evaluate_relevance(
                question=pair["question"],
                retrieved_context=pair["context"]
            )
            
            results.append({
                "index": i,
                "question": pair["question"][:100],
                **result
            })
        
        return results
    
    def get_summary_report(self) -> str:
        """Get a formatted summary report of relevance metrics."""
        metrics = self.get_relevance_metrics()
        
        if metrics["total_queries"] == 0:
            return "📊 No relevance evaluations recorded yet."
        
        report = f"""
📊 **RELEVANCE EVALUATION SUMMARY**

🔢 **Query Statistics:**
- Total Queries Evaluated: {metrics['total_queries']}
- Recent Queries Analyzed: {metrics['recent_queries_analyzed']}
- Average Relevance Score: {metrics['average_relevance']:.3f}

📈 **Relevance Distribution:**
- 🟢 High Relevance (≥0.7): {metrics['relevance_distribution']['high (≥0.7)']} queries
- 🟡 Medium Relevance (0.4-0.7): {metrics['relevance_distribution']['medium (0.4-0.7)']} queries  
- 🔴 Low Relevance (<0.4): {metrics['relevance_distribution']['low (<0.4)']} queries

📋 **Recent Evaluations Preview:**"""
        
        for query in metrics['recent_queries'][-5:]:  # Last 5
            score_emoji = "🟢" if query['score'] >= 0.7 else "🟡" if query['score'] >= 0.4 else "🔴"
            report += f"\n- {score_emoji} {query['score']:.2f} | {query['question'][:80]}..."
        
        return report


# Convenience function for quick evaluation
def quick_relevance_check(question: str, context: str, persist_directory: str = "./chroma_db") -> Dict[str, Any]:
    """Quick relevance evaluation without creating a persistent evaluator instance."""
    evaluator = RelevanceEvaluator(persist_directory)
    return evaluator.evaluate_relevance(question, context) 