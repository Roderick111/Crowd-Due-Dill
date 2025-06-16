/**
 * AuthButton.js - Authentication Button Component
 * Purpose: Displays login/logout button and user information when authenticated.
 * Provides visual feedback for authentication state and user profile access.
 */
const AuthButton = ({ showUserMenu, setShowUserMenu }) => {
    const { isAuthenticated, isLoading, user, login, logout } = useAuth();
    const [showDropdown, setShowDropdown] = React.useState(false);

    // Close dropdown when clicking outside
    React.useEffect(() => {
        const handleClickOutside = (event) => {
            if (showDropdown && !event.target.closest('.auth-dropdown')) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, [showDropdown]);

    // Show loading state
    if (isLoading) {
        return (
            <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gray-700 rounded-full animate-pulse"></div>
            </div>
        );
    }

    // Not authenticated - show login button
    if (!isAuthenticated) {
        return (
            <button
                onClick={login}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
            >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                <span>Sign In</span>
            </button>
        );
    }

    // Authenticated - show user avatar and dropdown
    return (
        <div className="relative auth-dropdown">
            <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="flex items-center space-x-3 p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
                {/* User Avatar */}
                <div className="w-8 h-8 rounded-full overflow-hidden bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                    {user?.picture ? (
                        <img 
                            src={user.picture} 
                            alt={user.name || user.email} 
                            className="w-full h-full object-cover"
                        />
                    ) : (
                        <span className="text-white font-bold text-sm">
                            {(user?.name || user?.email || 'U').charAt(0).toUpperCase()}
                        </span>
                    )}
                </div>

                {/* User Name/Email */}
                <div className="hidden md:block text-left">
                    <div className="text-sm font-medium text-white">
                        {user?.name || 'User'}
                    </div>
                    {user?.email && (
                        <div className="text-xs text-gray-400">
                            {user.email}
                        </div>
                    )}
                </div>

                {/* Dropdown Arrow */}
                <svg 
                    className={`w-4 h-4 text-gray-400 transition-transform ${showDropdown ? 'rotate-180' : ''}`} 
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Dropdown Menu */}
            {showDropdown && (
                <div className="absolute right-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg border border-gray-700 z-50">
                    <div className="p-4 border-b border-gray-700">
                        <div className="flex items-center space-x-3">
                            {/* Larger Avatar */}
                            <div className="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                                {user?.picture ? (
                                    <img 
                                        src={user.picture} 
                                        alt={user.name || user.email} 
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <span className="text-white font-bold text-lg">
                                        {(user?.name || user?.email || 'U').charAt(0).toUpperCase()}
                                    </span>
                                )}
                            </div>
                            
                            {/* User Info */}
                            <div className="flex-1">
                                <div className="text-sm font-medium text-white">
                                    {user?.name || 'User'}
                                </div>
                                {user?.email && (
                                    <div className="text-xs text-gray-400">
                                        {user.email}
                                    </div>
                                )}
                                {user?.email_verified && (
                                    <div className="flex items-center space-x-1 mt-1">
                                        <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-xs text-green-500">Verified</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                        <button
                            onClick={() => {
                                setShowDropdown(false);
                                // TODO: Open user preferences modal
                                console.log('Open user preferences');
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 flex items-center space-x-3"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <span>Preferences</span>
                        </button>

                        <button
                            onClick={() => {
                                setShowDropdown(false);
                                // TODO: Show user sessions
                                console.log('Show user sessions');
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 flex items-center space-x-3"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span>My Sessions</span>
                        </button>

                        <div className="border-t border-gray-700 mt-2 pt-2">
                            <button
                                onClick={() => {
                                    setShowDropdown(false);
                                    logout();
                                }}
                                className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-700 flex items-center space-x-3"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                                </svg>
                                <span>Sign Out</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}; 