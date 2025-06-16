const { useState } = React;

const MessageActions = ({ message, messageIndex, onAction }) => {
    const [showTooltip, setShowTooltip] = useState('');

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(message.content);
            setShowTooltip('copy');
            setTimeout(() => setShowTooltip(''), 1000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    const handleRegenerate = () => {
        onAction('regenerate', messageIndex);
    };

    const handleLike = () => {
        onAction('like', messageIndex);
        setShowTooltip('like');
        setTimeout(() => setShowTooltip(''), 1000);
    };

    const handleDislike = () => {
        onAction('dislike', messageIndex);
        setShowTooltip('dislike');
        setTimeout(() => setShowTooltip(''), 1000);
    };

    return (
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {/* Copy */}
            <div className="relative">
                <button
                    onClick={handleCopy}
                    className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                    title="Copy message"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                </button>
                {showTooltip === 'copy' && (
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded">
                        Copied!
                    </div>
                )}
            </div>

            {/* Regenerate */}
            <button
                onClick={handleRegenerate}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                title="Regenerate response"
            >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
            </button>

            {/* Like */}
            <div className="relative">
                <button
                    onClick={handleLike}
                    className="p-1.5 text-gray-400 hover:text-green-400 hover:bg-gray-700 rounded transition-colors"
                    title="Like message"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                    </svg>
                </button>
                {showTooltip === 'like' && (
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded">
                        Liked!
                    </div>
                )}
            </div>

            {/* Dislike */}
            <div className="relative">
                <button
                    onClick={handleDislike}
                    className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded transition-colors"
                    title="Dislike message"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v2a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10H5a2 2 0 00-2 2v6a2 2 0 002 2h2.5" />
                    </svg>
                </button>
                {showTooltip === 'dislike' && (
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded">
                        Disliked!
                    </div>
                )}
            </div>
        </div>
    );
};

// Export for use in other components
window.MessageActions = MessageActions; 