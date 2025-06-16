/**
 * TopBarUserProfile.js - Top Bar User Profile Component
 * Purpose: Shows user avatar in the top bar and handles profile menu.
 * Replaces hamburger menu and includes settings, archived sessions, and auth options.
 */
const TopBarUserProfile = ({ 
    showProfileMenu, 
    setShowProfileMenu,
    onOpenSettingsModal,

    onOpenArchivedModal 
}) => {
    const { isAuthenticated, isLoading, user, login, logout } = useAuth();
    const ARCHIVE_FEATURE_ENABLED = false; // TODO: Re-enable when multi-user auth implemented
    const [imageLoadError, setImageLoadError] = React.useState(false);

    // Reset image error when user changes
    React.useEffect(() => {
        setImageLoadError(false);
    }, [user?.picture]);

    // Show loading state
    if (isLoading) {
        return (
            <div className="w-8 h-8 bg-gray-700 rounded-full animate-pulse"></div>
        );
    }

    // Get user initials for fallback
    const getUserInitials = () => {
        if (user?.name) {
            return user.name.split(' ').map(n => n.charAt(0)).join('').toUpperCase().substring(0, 2);
        } else if (user?.email) {
            return user.email.charAt(0).toUpperCase();
        }
        return 'U';
    };

    // Handle image load error
    const handleImageError = () => {
        setImageLoadError(true);
    };

    return (
        <div className="relative">
            {/* User Avatar Button */}
            <button
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity overflow-hidden"
            >
                {isAuthenticated && user?.picture && !imageLoadError ? (
                    <img 
                        src={user.picture} 
                        alt={user.name || user.email || 'User'} 
                        className="w-full h-full object-cover"
                        onError={handleImageError}
                        onLoad={() => setImageLoadError(false)}
                    />
                ) : isAuthenticated ? (
                    <span className="text-white font-bold text-sm">
                        {getUserInitials()}
                    </span>
                ) : (
                    <span className="text-white font-bold text-sm">U</span>
                )}
            </button>

            {/* Profile Dropdown Menu */}
            {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg border border-gray-700 z-50">
                    {/* User Info Section (if authenticated) */}
                    {isAuthenticated && (
                        <>
                            <div className="px-4 py-3 border-b border-gray-700">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center overflow-hidden">
                                        {user?.picture && !imageLoadError ? (
                                            <img 
                                                src={user.picture} 
                                                alt={user.name || user.email || 'User'} 
                                                className="w-full h-full object-cover"
                                                onError={handleImageError}
                                                onLoad={() => setImageLoadError(false)}
                                            />
                                        ) : (
                                            <span className="text-white font-bold text-sm">
                                                {getUserInitials()}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="text-sm font-medium text-white truncate">
                                            {user?.name || 'User'}
                                        </div>
                                        {user?.email && (
                                            <div className="text-xs text-gray-400 truncate">
                                                {user.email}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </>
                    )}

                    {/* Menu Items */}
                    <div className="py-1">
                        <button
                            onClick={() => {
                                onOpenSettingsModal();
                                setShowProfileMenu(false);
                            }}
                            className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <span>Settings</span>
                        </button>
                        


                        {ARCHIVE_FEATURE_ENABLED && (
                            <button
                                onClick={() => {
                                    onOpenArchivedModal();
                                    setShowProfileMenu(false);
                                }}
                                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8l4 4 4-4m6 5l-3 3-3-3" />
                                </svg>
                                <span>Archived Sessions</span>
                            </button>
                        )}

                        {/* Authentication Section */}
                        <div className="border-t border-gray-700 pt-1">
                            {isAuthenticated ? (
                                <button
                                    onClick={() => {
                                        logout();
                                        setShowProfileMenu(false);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2 text-red-400"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                                    </svg>
                                    <span>Sign Out</span>
                                </button>
                            ) : (
                                <button
                                    onClick={() => {
                                        login();
                                        setShowProfileMenu(false);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700 flex items-center space-x-2 text-blue-400"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                                    </svg>
                                    <span>Sign In</span>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}; 