#!/usr/bin/env python3
"""
Test script for the standalone Relevance Evaluator.

This demonstrates how to use the separated relevance evaluation system
for optional assessment of RAG retrieval quality.
"""

import os
from dotenv import load_dotenv
from contextual_rag import OptimizedContextualRAGSystem
from relevance_evaluator import RelevanceEvaluator, quick_relevance_check

# Load environment variables
load_dotenv()

def test_standalone_relevance_evaluator():
    """Test the standalone relevance evaluator independently."""
    print("🧪 Testing Standalone Relevance Evaluator")
    print("=" * 50)
    
    # Initialize the evaluator
    evaluator = RelevanceEvaluator()
    
    # Example question and context
    test_question = "What are the benefits of meditation for anxiety?"
    test_context = """
    Context: This section discusses various therapeutic approaches for mental health.
    
    Content: Meditation has been shown to significantly reduce anxiety levels in clinical studies. 
    Regular mindfulness practice can help individuals develop better emotional regulation and stress management skills. 
    The practice involves focusing attention on the present moment, which helps break cycles of anxious thinking.
    Studies show that just 10 minutes of daily meditation can reduce cortisol levels and improve overall mental well-being.
    """
    
    # Test single evaluation
    print("📊 Single Relevance Evaluation:")
    result = evaluator.evaluate_relevance(test_question, test_context)
    
    print(f"✅ Success: {result['success']}")
    print(f"📈 Relevance Score: {result['relevance_score']:.3f}")
    print(f"💭 Reasoning: {result['relevance_details']['reasoning']}")
    print()
    
    # Test quick evaluation function
    print("⚡ Quick Relevance Check:")
    quick_result = quick_relevance_check(test_question, test_context)
    print(f"📈 Quick Score: {quick_result['relevance_score']:.3f}")
    print()
    
    return evaluator

def test_rag_with_optional_relevance():
    """Test RAG system with optional relevance evaluation."""
    print("🔗 Testing RAG + Optional Relevance Evaluation")
    print("=" * 50)
    
    # Initialize systems
    rag_system = OptimizedContextualRAGSystem()
    evaluator = RelevanceEvaluator()
    
    # Check if documents are loaded
    if not rag_system.vectorstore:
        print("⚠️ No documents loaded in RAG system. Loading sample document...")
        # You would load your documents here
        print("📄 Please load documents first using: rag_system.load_and_process_documents('path/to/doc')")
        return
    
    # Test questions
    test_questions = [
        "What are the benefits of meditation?",
        "How can I manage anxiety?",
        "What is the meaning of life?"  # Potentially low relevance
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Query {i}: {question}")
        print("-" * 30)
        
        # Get RAG answer (fast - no relevance evaluation)
        print("⚡ Getting RAG answer...")
        answer = rag_system.query(question)
        print(f"💬 Answer: {answer[:100]}...")
        
        # Optional: Get retrieval info for relevance evaluation
        print("\n📊 Optional: Evaluating relevance...")
        retrieval_info = rag_system.get_retrieval_info(question)
        
        if 'retrieved_documents' in retrieval_info:
            # Combine retrieved documents for evaluation
            combined_context = "\n\n".join(retrieval_info['retrieved_documents'])
            
            # Evaluate relevance separately
            relevance_result = evaluator.evaluate_relevance(question, combined_context)
            
            score = relevance_result['relevance_score']
            score_emoji = "🟢" if score >= 0.7 else "🟡" if score >= 0.4 else "🔴"
            
            print(f"{score_emoji} Relevance Score: {score:.3f}")
            print(f"💭 Reasoning: {relevance_result['relevance_details']['reasoning']}")

def test_batch_evaluation():
    """Test batch relevance evaluation."""
    print("\n📦 Testing Batch Relevance Evaluation")
    print("=" * 50)
    
    evaluator = RelevanceEvaluator()
    
    # Sample question-context pairs
    qa_pairs = [
        {
            "question": "How does meditation help with stress?",
            "context": "Meditation reduces cortisol levels and activates the parasympathetic nervous system, leading to relaxation and stress reduction."
        },
        {
            "question": "What is quantum physics?", 
            "context": "Meditation has been shown to significantly reduce anxiety levels in clinical studies."
        },
        {
            "question": "Benefits of mindfulness practice?",
            "context": "Regular mindfulness practice helps develop emotional regulation, improves focus, and reduces anxiety symptoms."
        }
    ]
    
    # Run batch evaluation
    results = evaluator.batch_evaluate_relevance(qa_pairs)
    
    print("\n📊 Batch Results:")
    for result in results:
        score = result['relevance_score']
        score_emoji = "🟢" if score >= 0.7 else "🟡" if score >= 0.4 else "🔴"
        print(f"{score_emoji} Q{result['index']+1}: {score:.3f} | {result['question'][:50]}...")

def test_metrics_and_reporting():
    """Test metrics collection and reporting."""
    print("\n📈 Testing Metrics and Reporting")
    print("=" * 50)
    
    evaluator = RelevanceEvaluator()
    
    # Get current metrics
    metrics = evaluator.get_relevance_metrics()
    
    print(f"📊 Total Evaluations: {metrics['total_queries']}")
    print(f"📈 Average Relevance: {metrics['average_relevance']:.3f}")
    print(f"📋 Distribution: {metrics['relevance_distribution']}")
    
    # Get summary report
    print("\n📋 Summary Report:")
    print(evaluator.get_summary_report())

if __name__ == "__main__":
    print("🧪 RELEVANCE EVALUATOR TEST SUITE")
    print("=" * 60)
    print("This demonstrates the separated relevance evaluation system.")
    print("The main RAG workflow is now faster without relevance evaluation,")
    print("but you can still assess quality using this standalone evaluator.\n")
    
    try:
        # Test 1: Standalone evaluator
        evaluator = test_standalone_relevance_evaluator()
        
        # Test 2: RAG with optional relevance
        test_rag_with_optional_relevance()
        
        # Test 3: Batch evaluation
        test_batch_evaluation()
        
        # Test 4: Metrics and reporting
        test_metrics_and_reporting()
        
        print("\n✅ All tests completed successfully!")
        print("\n💡 Usage Tips:")
        print("- Use the main RAG system for fast queries")
        print("- Use RelevanceEvaluator for quality assessment")
        print("- Run batch evaluations to monitor system performance")
        print("- Check metrics periodically to ensure good retrieval quality")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n🔧 Make sure you have:")
        print("- Set up your .env file with API keys")
        print("- Loaded documents into the RAG system")
        print("- Installed all required dependencies") 