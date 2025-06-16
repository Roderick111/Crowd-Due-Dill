/**
 * ArchivedSessions.js - Archived Sessions Modal
 * Purpose: Displays archived sessions with options to view, unarchive, or permanently delete.
 * Accessible through the Profile dropdown menu for clean session management.
 */
const { useState, useEffect } = React;

const ArchivedSessions = ({
    showArchivedModal,
    setShowArchivedModal,
    onLoadSession,
    onDeleteSession
}) => {
    // State for archived sessions
    const [archivedSessions, setArchivedSessions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    // Fetch archived sessions when modal opens
    useEffect(() => {
        if (showArchivedModal) {
            fetchArchivedSessions();
        }
    }, [showArchivedModal]);

    const fetchArchivedSessions = async () => {
        setIsLoading(true);
        try {
            const sessions = await apiService.fetchArchivedSessions();
            setArchivedSessions(sessions);
        } catch (error) {
            console.error('Error fetching archived sessions:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleUnarchive = async (sessionId) => {
        try {
            await apiService.unarchiveSession(sessionId);
            // Remove from archived list
            setArchivedSessions(prev => prev.filter(s => s.session_id !== sessionId));
        } catch (error) {
            console.error('Error unarchiving session:', error);
        }
    };

    const handleDelete = async (sessionId) => {
        if (!confirm('Are you sure you want to permanently delete this archived session? This action cannot be undone.')) {
            return;
        }
        
        try {
            await onDeleteSession(sessionId);
            // Remove from archived list
            setArchivedSessions(prev => prev.filter(s => s.session_id !== sessionId));
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    };

    const handleViewSession = (sessionId) => {
        onLoadSession(sessionId);
        setShowArchivedModal(false);
    };

    // Filter sessions based on search
    const filteredSessions = archivedSessions.filter(session => {
        if (!searchTerm) return true;
        const title = session.title || `Session ${session.session_id.slice(0, 8)}`;
        return title.toLowerCase().includes(searchTerm.toLowerCase());
    });

    if (!showArchivedModal) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-gray-800 rounded-lg shadow-lg w-full max-w-4xl h-3/4 flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-700">
                    <h2 className="text-xl font-semibold text-white">Archived Sessions</h2>
                    <button
                        onClick={() => setShowArchivedModal(false)}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Search */}
                <div className="p-4 border-b border-gray-700">
                    <input
                        type="text"
                        placeholder="Search archived sessions..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-gray-700 text-white text-sm px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
                    />
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    {isLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="text-gray-400">Loading archived sessions...</div>
                        </div>
                    ) : filteredSessions.length === 0 ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="text-gray-400">
                                {searchTerm ? `No archived sessions found matching "${searchTerm}"` : 'No archived sessions'}
                            </div>
                        </div>
                    ) : (
                        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                            {filteredSessions.map(session => (
                                <div key={session.session_id} className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors">
                                    {/* Session Info */}
                                    <div className="mb-3">
                                        <h3 className="font-medium text-white truncate mb-1">
                                            {session.title || `Session ${session.session_id.slice(0, 8)}`}
                                        </h3>
                                        <div className="text-xs text-gray-400 space-y-1">
                                            <div>{session.message_count} messages</div>
                                            <div>Created: {new Date(session.created_at).toLocaleDateString()}</div>
                                            <div>Domains: {session.domains?.length > 0 ? session.domains.join(', ') : 'None'}</div>
                                        </div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => handleViewSession(session.session_id)}
                                            className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors flex items-center justify-center space-x-1"
                                        >
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                            <span>View</span>
                                        </button>
                                        <button
                                            onClick={() => handleUnarchive(session.session_id)}
                                            className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors flex items-center justify-center space-x-1"
                                        >
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v0H8v0z" />
                                            </svg>
                                            <span>Restore</span>
                                        </button>
                                        <button
                                            onClick={() => handleDelete(session.session_id)}
                                            className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors flex items-center justify-center"
                                        >
                                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-700 bg-gray-750">
                    <div className="text-xs text-gray-400 text-center">
                        {filteredSessions.length} archived session{filteredSessions.length !== 1 ? 's' : ''} found
                    </div>
                </div>
            </div>
        </div>
    );
};

// Export for use in other components
window.ArchivedSessions = ArchivedSessions; 