/**
 * ChatArea.js - Main Chat Interface (Lightweight Version)
 * Purpose: Displays message history, handles user input, and shows conversation starters.
 * Manages chat flow with loading states, auto-scroll, and suggestion integration.
 */

// Simple Markdown renderer for agent messages
const MessageContent = ({ content }) => {
    // Process markdown with proper list handling
    const processMarkdown = (text) => {
        // Split into lines for better processing
        const lines = text.split('\n');
        const processed = [];
        let inList = false;
        let listType = null;

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            
            // Handle headers
            if (line.startsWith('### ')) {
                if (inList) {
                    processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                    inList = false;
                }
                let headerText = line.substring(4)
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')
                    .replace(/\*([^*]+?)\*/g, '<em class="italic">$1</em>');
                processed.push(`<h3 class="text-lg font-semibold mt-0 mb-0 pt-2 text-white">${headerText}</h3>`);
            } else if (line.startsWith('## ')) {
                if (inList) {
                    processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                    inList = false;
                }
                let headerText = line.substring(3)
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')
                    .replace(/\*([^*]+?)\*/g, '<em class="italic">$1</em>');
                processed.push(`<h2 class="text-xl font-bold mt-2 mb-0 pt-3 text-white">${headerText}</h2>`);
            }
            // Handle bullet points
            else if (line.match(/^[•\-\*] /)) {
                if (!inList || listType !== 'ul') {
                    if (inList) processed.push('</ol>');
                    processed.push('<ul class="list-disc mt-0 ml-6 mb-6">');
                    inList = true;
                    listType = 'ul';
                }
                let content = line.substring(2).trim()
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>')
                    .replace(/\*([^*]+?)\*/g, '<em class="italic text-gray-300">$1</em>');
                processed.push(`<li class="mb-2">${content}</li>`);
            }
            // Handle numbered lists
            else if (line.match(/^\d+\. /)) {
                if (!inList || listType !== 'ol') {
                    if (inList) processed.push('</ul>');
                    processed.push('<ol class="list-decimal mt-0 ml-6 mb-6">');
                    inList = true;
                    listType = 'ol';
                }
                let content = line.replace(/^\d+\. /, '')
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>')
                    .replace(/\*([^*]+?)\*/g, '<em class="italic text-gray-300">$1</em>');
                processed.push(`<li class="mb-2">${content}</li>`);
            }
            // Regular text
            else {
                if (inList && line.trim() === '') {
                    // Keep empty lines in lists
                    continue;
                } else if (inList && line.trim() !== '') {
                    // Close list if we hit non-list content
                    processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                    inList = false;
                    listType = null;
                }
                
                if (line.trim() === '') {
                    processed.push('<br>');
                } else {
                    // Process inline formatting - handle bold first, then italic to avoid conflicts
                    line = line
                        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>')
                        .replace(/\*([^*]+?)\*/g, '<em class="italic text-gray-300">$1</em>');
                    processed.push(`<p class="mb-1 pb-1">${line}</p>`);
                }
            }
        }

        // Close any open lists
        if (inList) {
            processed.push(listType === 'ul' ? '</ul>' : '</ol>');
        }

        return processed.join('');
    };

    const processedContent = processMarkdown(content);

    return (
        <div 
            className="max-w-none leading-relaxed"
            dangerouslySetInnerHTML={{ __html: processedContent }}
        />
    );
};
const ChatArea = ({
    messages,
    isLoading,
    inputValue,
    setInputValue,
    onSendMessage,
    messagesEndRef,
    inputRef,
    // Conversation starters props
    systemStatus,
    isNewSession,
    suggestionsDismissed,
    selectedSuggestion,
    onSuggestionClick,
    onDismissSuggestions,
    // Message actions
    onMessageAction
}) => {
    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        onSendMessage(inputValue);
    };

    // Handle message actions
    const handleMessageAction = (action, messageIndex) => {
        if (onMessageAction) {
            onMessageAction(action, messageIndex, messages[messageIndex]);
        }
    };

    // Show suggestions for new sessions unless manually dismissed
    const showSuggestions = isNewSession && !suggestionsDismissed;

    return (
        <div className="flex flex-col h-full">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-6 pt-20 min-h-0">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.length === 0 ? (
                        <div className="text-center text-gray-400 mt-20">
                            <h2 className="text-2xl font-semibold mb-2 text-gray-300">
                                {isNewSession ? "Professional Crowdfunding Due Diligence Advisory" : "How can I help you today?"}
                            </h2>
                            <p className="text-gray-400">
                                {isNewSession ? "Get expert guidance on crowdfunding regulations, compliance, and legal requirements" : "Continue your consultation with your Crowdfunding Advisor"}
                            </p>
                            
                            {/* Suggested prompts for new sessions */}
                            {showSuggestions && (
                                <ConversationStarters 
                                    systemStatus={systemStatus}
                                    isLoading={isLoading}
                                    onSuggestionClick={onSuggestionClick}
                                    onDismiss={onDismissSuggestions}
                                    selectedSuggestion={selectedSuggestion}
                                />
                            )}
                        </div>
                    ) : (
                        messages.map((message, index) => (
                            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`${
                                    message.role === 'user' 
                                        ? 'max-w-lg bg-blue-600 text-white p-4 rounded-lg ml-12' 
                                        : 'max-w-4xl text-gray-100 mr-12 group relative'
                                }`}>
                                    {message.role === 'user' ? (
                                        <div className="text-left">{message.content}</div>
                                    ) : (
                                        <div className="relative">
                                            <MessageContent content={message.content} />
                                            {/* Message Actions - appears on hover at bottom left */}
                                            <div className="absolute -bottom-6 left-0">
                                                <MessageActions 
                                                    message={message}
                                                    messageIndex={index}
                                                    onAction={handleMessageAction}
                                                />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                    
                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="max-w-4xl text-gray-100 mr-12">
                                <div className="flex space-x-1">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-700 p-4 flex-shrink-0">
                <div className="max-w-4xl mx-auto">
                    <form onSubmit={handleSubmit} className="flex space-x-4">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder={isNewSession && !suggestionsDismissed ? "Ask about crowdfunding regulations, compliance requirements, or legal guidance..." : "Message Crowdfunding Advisor..."}
                            className="flex-1 bg-gray-800 text-white border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !inputValue.trim()}
                            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

// Export for use in other components
window.ChatArea = ChatArea; 