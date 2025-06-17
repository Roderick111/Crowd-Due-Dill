/**
 * useAppLogic.js - Business Logic Hook
 * Purpose: Contains ALL application state, side effects, and business functions.
 * Provides clean interface to App component for complete separation of concerns.
 */
const { useState, useEffect, useRef } = React;

const useAppLogic = () => {
    // State management
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [systemStatus, setSystemStatus] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [showSettingsModal, setShowSettingsModal] = useState(false);

    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const [showArchivedModal, setShowArchivedModal] = useState(false);
    
    // Session-based conversation starter state
    const [suggestionsDismissed, setSuggestionsDismissed] = useState(false);
    const [selectedSuggestion, setSelectedSuggestion] = useState(null);

    // Refs
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Check if this is a new session (no messages)
    const isNewSession = messages.length === 0;
    
    // Show suggestions for new sessions unless manually dismissed for this session
    const showSuggestions = isNewSession && !suggestionsDismissed;

    // Handle suggestion click with visual feedback
    const handleSuggestionClick = (suggestion) => {
        setSelectedSuggestion(suggestion);
        setInputValue(suggestion);
        
        // Clear selection after a brief moment
        setTimeout(() => {
            setSelectedSuggestion(null);
        }, 200);
    };

    // Handle dismissing suggestions for current session
    const dismissSuggestions = () => {
        setSuggestionsDismissed(true);
    };

    // Modal handlers
    const openSettingsModal = () => {
        setShowSettingsModal(true);
    };



    const openArchivedModal = () => {
        setShowArchivedModal(true);
        setShowProfileMenu(false); // Close profile menu when opening archived modal
    };

    // Reset suggestions when starting a new session
    useEffect(() => {
        if (messages.length === 0) {
            setSuggestionsDismissed(false);
        }
    }, [currentSessionId]); // Reset when session changes

    // Scroll to bottom of messages - always instant
    const scrollToBottom = () => {
        const chatContainer = messagesEndRef.current?.closest('.overflow-y-auto');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Fetch system status
    const fetchSystemStatus = async () => {
        try {
            const data = await apiService.fetchSystemStatus();
            setSystemStatus(data);
        } catch (error) {
            console.error('Error fetching system status:', error);
        }
    };

    // Fetch sessions
    const fetchSessions = async () => {
        try {
            // Check Auth0 authentication state directly
            const authState = await window.authStateManager.getAuthState();
            console.log('Auth state for session fetch:', authState);
            
            if (authState.isAuthenticated && authState.user && authState.accessToken) {
                // Fetch user-specific sessions for authenticated users
                console.log('Fetching user-specific sessions for:', authState.user.email);
                const data = await apiService.fetchUserSessions();
                console.log('Fetched user sessions:', data);
                setSessions(data.sessions || []);
            } else {
                // Fetch anonymous sessions only for non-authenticated users
                console.log('Fetching anonymous sessions (user not authenticated)');
                const data = await apiService.fetchSessions();
                console.log('Fetched anonymous sessions:', data);
                setSessions(data || []);
            }
        } catch (error) {
            console.error('Error fetching sessions:', error);
            // Fallback to anonymous sessions on error
            try {
                const data = await apiService.fetchSessions();
                setSessions(data || []);
            } catch (fallbackError) {
                console.error('Error fetching fallback sessions:', fallbackError);
                setSessions([]);
            }
        }
    };

    // Handle payment results on page load
    useEffect(() => {
        const handlePaymentResults = async () => {
            try {
                // Wait for stripe service to initialize
                await window.stripeService?.initPromise;
                
                const paymentResult = await window.stripeService?.handlePaymentResult();
                if (paymentResult) {
                    if (paymentResult.status === 'success') {
                        alert(`🎉 ${paymentResult.message}\n\nWelcome to Premium! Your enhanced regulatory guidance experience begins now.`);
                    } else if (paymentResult.status === 'canceled') {
                        // Optionally show a more subtle notification
                        console.log('Payment canceled by user');
                    }
                }
            } catch (error) {
                console.error('Error handling payment result:', error);
            }
        };

        handlePaymentResults();
    }, []);

    // Initial data load
    useEffect(() => {
        fetchSystemStatus();
        fetchSessions();
    }, []);

    // Auto-load messages when switching to a session that has messages
    useEffect(() => {
        const selectedSession = sessions.find(s => s.session_id === currentSessionId);
        if (selectedSession && selectedSession.message_count > 0 && messages.length === 0) {
            console.log(`Auto-loading messages for session ${currentSessionId} (${selectedSession.message_count} messages)`);
            loadSessionMessages(currentSessionId);
        }
    }, [currentSessionId, sessions, messages.length]);

    // Generate meaningful session title from first message
    const generateSessionTitle = (firstMessage) => {
        if (!firstMessage) return 'New Session';
        
        // Clean and truncate the message
        const cleanMessage = firstMessage.trim().replace(/\n+/g, ' ');
        if (cleanMessage.length <= 40) return cleanMessage;
        
        // Find a good breaking point
        const truncated = cleanMessage.substring(0, 40);
        const lastSpace = truncated.lastIndexOf(' ');
        return lastSpace > 20 ? truncated.substring(0, lastSpace) + '...' : truncated + '...';
    };

    // Send message to chat API
    const sendMessage = async (message) => {
        if (!message.trim()) return;

        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const data = await apiService.sendMessage(message, currentSessionId);
            
            const assistantMessage = {
                role: 'assistant',
                content: data.response,
                timestamp: data.timestamp,
                metadata: {
                    message_type: data.message_type,
                    rag_used: data.rag_used,
                    cache_hit: data.cache_hit,
                }
            };

            setMessages(prev => [...prev, assistantMessage]);
            setCurrentSessionId(data.session_id);
            
            // If this was the first message, update session title
            if (messages.length === 0) {
                await updateSessionTitle(data.session_id, generateSessionTitle(message));
            }
            
            // Refresh sessions to update message count
            await fetchSessions();
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'assistant',
                content: `❌ Error: ${error.message}`,
                timestamp: new Date().toISOString(),
                isError: true,
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };



    // Create new session
    const createNewSession = async () => {
        try {
            setMessages([]);
            setCurrentSessionId(null);
            setSuggestionsDismissed(false); // Reset suggestions for new session
            await fetchSessions();
        } catch (error) {
            console.error('Error creating new session:', error);
        }
    };

    // Load session messages
    const loadSessionMessages = async (sessionId) => {
        try {
            console.log(`Loading messages for session: ${sessionId}`);
            
            const data = await apiService.loadSessionMessages(sessionId);
            console.log(`Loaded ${data.messages?.length || 0} messages for session ${sessionId}`);
            
            if (data.messages && Array.isArray(data.messages)) {
                setMessages(data.messages);
                setCurrentSessionId(sessionId);
            } else {
                console.warn('No messages found in session data:', data);
                setMessages([]);
                setCurrentSessionId(sessionId);
            }
        } catch (error) {
            console.error('Error loading session messages:', error);
            setMessages([]);
        }
    };

    // Update session title
    const updateSessionTitle = async (sessionId, title) => {
        try {
            await apiService.updateSessionTitle(sessionId, title);
            await fetchSessions();
        } catch (error) {
            console.error('Error updating session title:', error);
        }
    };

    // Archive session
    const archiveSession = async (sessionId) => {
        try {
            await apiService.archiveSession(sessionId);
            await fetchSessions();
            if (currentSessionId === sessionId) {
                setMessages([]);
                setCurrentSessionId(null);
            }
        } catch (error) {
            console.error('Error archiving session:', error);
        }
    };

    // Delete session
    const deleteSession = async (sessionId) => {
        if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
            return;
        }
        
        try {
            await apiService.deleteSession(sessionId);
            await fetchSessions();
            if (currentSessionId === sessionId) {
                setMessages([]);
                setCurrentSessionId(null);
            }
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    };

    // Handle message actions (copy, regenerate, bookmark, like, dislike)
    const handleMessageAction = async (action, messageIndex, message) => {
        console.log(`Message action: ${action} on message ${messageIndex}`);
        
        switch (action) {
            case 'regenerate':
                if (messageIndex > 0) {
                    // Get the user message that prompted this response
                    const userMessage = messages[messageIndex - 1];
                    if (userMessage && userMessage.role === 'user') {
                        // Remove messages from this point forward and regenerate
                        const messagesToKeep = messages.slice(0, messageIndex);
                        setMessages(messagesToKeep);
                        await sendMessage(userMessage.content);
                    }
                }
                break;
                
            case 'bookmark':
                // TODO: Implement bookmark functionality
                console.log('Bookmarking message:', message.content.substring(0, 50) + '...');
                break;
                
            case 'like':
                // TODO: Implement like functionality (could send feedback to backend)
                console.log('Liked message:', messageIndex);
                break;
                
            case 'dislike':
                // TODO: Implement dislike functionality (could send feedback to backend)
                console.log('Disliked message:', messageIndex);
                break;
                
            default:
                console.log('Unknown action:', action);
        }
    };

    // Return all state and functions needed by the App component
    return {
        // State
        messages,
        inputValue,
        setInputValue,
        isLoading,
        systemStatus,
        sessions,
        currentSessionId,
        sidebarOpen,
        setSidebarOpen,
        showSettingsModal,
        setShowSettingsModal,

        showProfileMenu,
        setShowProfileMenu,
        showArchivedModal,
        setShowArchivedModal,
        suggestionsDismissed,
        selectedSuggestion,
        isNewSession,
        showSuggestions,
        
        // Refs
        messagesEndRef,
        inputRef,
        
        // Functions
        handleSuggestionClick,
        dismissSuggestions,
        openSettingsModal,

        openArchivedModal,
        sendMessage,

        createNewSession,
        loadSessionMessages,
        updateSessionTitle,
        archiveSession,
        deleteSession,
        handleMessageAction
    };
};

// Export for use in other components
window.useAppLogic = useAppLogic; 