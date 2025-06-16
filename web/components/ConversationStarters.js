/**
 * ConversationStarters.js - Dynamic Conversation Prompts
 * Purpose: Generates domain-specific question suggestions using Fisher-Yates shuffle.
 * Provides 4 randomized conversation starters based on currently active knowledge domains.
 */
const ConversationStarters = ({ 
    systemStatus, 
    isLoading, 
    onSuggestionClick, 
    onDismiss,
    selectedSuggestion 
}) => {
    const [currentSuggestions, setCurrentSuggestions] = React.useState([]);

    // Crowdfunding due diligence conversation starters
    const conversationStarters = {
        eu_crowdfunding: [
            "What are the key requirements for crowdfunding platforms under EU Regulation 2020/1503?",
            "How do investor protection measures work in crowdfunding?",
            "What are the disclosure requirements for crowdfunding project owners?",
            "What are the investment limits for different types of investors?",
            "How does the cross-border passport system work for crowdfunding platforms?",
            "What are the authorization requirements for crowdfunding service providers?",
            "How are retail and sophisticated investors defined in the regulation?",
            "What are the key differences between loan-based and investment-based crowdfunding?",
            "What complaints handling procedures must platforms implement?",
            "How does the regulation address conflicts of interest in crowdfunding?"
        ],
        general: [
            "I need help understanding crowdfunding regulations for my platform",
            "What compliance requirements should I be aware of when starting a crowdfunding business?",
            "Help me understand the regulatory framework for cross-border crowdfunding",
            "I'm confused about investor protection requirements - can you clarify?",
            "What are the main regulatory risks in crowdfunding operations?",
            "I need guidance on disclosure requirements for crowdfunding projects",
            "How do I ensure my crowdfunding platform complies with EU regulations?",
            "What are the authorization procedures for crowdfunding service providers?",
            "Help me understand the differences between retail and sophisticated investor rules",
            "I need clarity on the regulatory requirements for loan-based crowdfunding"
        ]
    };

    // Fisher-Yates shuffle algorithm for unbiased random selection
    const shuffleArray = (array) => {
        const shuffled = [...array]; // Create a copy to avoid modifying original
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    };

    // Get 4 suggestions: 2 from crowdfunding regulations + 2 from general queries
    const getConversationSuggestions = () => {
        // Always use eu_crowdfunding domain since it's our only domain
        const crowdfundingQuestions = conversationStarters.eu_crowdfunding;
        const generalQuestions = conversationStarters.general;
        
        // Get 2 random questions from each category
        const selectedCrowdfundingQuestions = shuffleArray(crowdfundingQuestions).slice(0, 2);
        const selectedGeneralQuestions = shuffleArray(generalQuestions).slice(0, 2);
        
        // Combine and return 4 total questions
        return [...selectedCrowdfundingQuestions, ...selectedGeneralQuestions];
    };

    // Generate initial suggestions when component mounts
    React.useEffect(() => {
        if (currentSuggestions.length === 0) {
            const initialSuggestions = getConversationSuggestions();
            setCurrentSuggestions(initialSuggestions);
        }
    }, []);

    return (
        <div className="mt-10 space-y-3">
            <div className="flex items-center justify-between max-w-lg mx-auto mb-3">
                <p className="text-sm text-gray-400">
                    Try asking about crowdfunding regulations:
                </p>
                <button
                    onClick={onDismiss}
                    className="text-xs text-gray-500 hover:text-gray-300 transition-colors px-2 py-1 hover:bg-gray-800 rounded"
                    title="Hide suggestions for this session"
                >
                    ✕
                </button>
            </div>
            <div className="space-y-2">
                {currentSuggestions.length === 0 ? (
                    <div className="text-center text-gray-400 text-sm py-4">
                        Loading suggestions...
                    </div>
                ) : (
                    currentSuggestions.map((prompt, index) => (
                        <button
                            key={index}
                            onClick={() => onSuggestionClick(prompt)}
                            disabled={isLoading}
                            className={`block w-full max-w-lg mx-auto p-3 rounded-lg text-sm text-left transition-all duration-200 ${
                                selectedSuggestion === prompt
                                    ? 'bg-blue-600 text-white transform scale-[0.98]'
                                    : 'bg-gray-800 hover:bg-gray-700 hover:scale-[1.01]'
                            } ${
                                isLoading ? 'opacity-50 cursor-not-allowed' : ''
                            }`}
                        >
                            <span className="flex items-center">
                                {selectedSuggestion === prompt && (
                                    <span className="mr-2 animate-spin">⟳</span>
                                )}
                                "{prompt}"
                            </span>
                        </button>
                    ))
                )}
            </div>
        </div>
    );
};

// Export for use in other components
window.ConversationStarters = ConversationStarters; 