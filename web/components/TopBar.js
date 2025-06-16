/**
 * TopBar.js - Application Header
 * Purpose: Displays current session info, sidebar toggle, and user profile menu.
 * Handles navigation controls and modal triggers for settings information.
 */
const TopBar = ({
    sidebarOpen,
    setSidebarOpen,
    currentSessionId,
    sessions,
    showProfileMenu,
    setShowProfileMenu,
    onOpenSettingsModal,

    onOpenArchivedModal,
    systemStatus
}) => {
    // TODO: Re-enable archive feature when multi-user authentication is implemented
    const ARCHIVE_FEATURE_ENABLED = false;

    // Get current session title for display
    const getCurrentSessionTitle = () => {
        if (!currentSessionId) return 'New Session';
        
        const currentSession = sessions.find(s => s.session_id === currentSessionId);
        return currentSession?.title || `Session ${currentSessionId.slice(0, 8)}`;
    };

    return (
        <div className="bg-transparent h-16 px-4 grid grid-cols-3 items-center">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
                {/* Sidebar Toggle */}
                {!sidebarOpen && (
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 hover:bg-gray-700 rounded"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <rect x="3" y="3" width="6" height="18" rx="2" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}/>
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8M13 12h8M13 17h8" />
                        </svg>
                    </button>
                )}

                {/* Domain Status Display - Single Domain */}
                <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-700 rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span>EU Crowdfunding Regulations</span>
                </div>
            </div>

            {/* Center Section - Empty */}
            <div className="text-center">
            </div>

            {/* Right Section - Theme Switcher + User Profile */}
            <div className="flex justify-end items-center space-x-3">
                {/* Theme Switcher */}
                <ThemeSwitcher />
                
                {/* User Profile Icon with Menu */}
                <TopBarUserProfile 
                    showProfileMenu={showProfileMenu}
                    setShowProfileMenu={setShowProfileMenu}
                    onOpenSettingsModal={onOpenSettingsModal}

                    onOpenArchivedModal={onOpenArchivedModal}
                />
            </div>


        </div>
    );
};

// Export for use in other components
window.TopBar = TopBar; 