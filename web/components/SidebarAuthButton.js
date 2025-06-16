/**
 * SidebarAuthButton.js - Sidebar Premium Button Component
 * Purpose: Shows sign-in button for anonymous users and Go Premium button for authenticated users.
 * Profile management is now handled via the top bar user profile dropdown.
 */
const SidebarAuthButton = () => {
    const { isAuthenticated, isLoading, login } = useAuth();
    const [showPremiumModal, setShowPremiumModal] = React.useState(false);

    // Show loading state
    if (isLoading) {
        return (
            <div className="w-full p-3 bg-gray-700 rounded-lg animate-pulse">
                <div className="h-4 bg-gray-600 rounded"></div>
            </div>
        );
    }

    // Not authenticated - show login button
    if (!isAuthenticated) {
        return (
            <button
                onClick={login}
                className="w-full flex items-center justify-center space-x-2 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
            >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                <span>Sign In</span>
            </button>
        );
    }

    // Authenticated - Go Premium button temporarily disabled
    const handleGoPremium = () => {
        setShowPremiumModal(true);
    };

    return (
        <>
            {/* Go Premium button temporarily disabled */}
            {false && (
                <button
                    onClick={handleGoPremium}
                    className="w-full flex items-center justify-center space-x-2 p-3 go-premium-button text-white rounded-lg transition-colors text-sm font-medium"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                    <span>Go Premium</span>
                </button>
            )}

            <PremiumModal 
                isOpen={showPremiumModal} 
                onClose={() => setShowPremiumModal(false)} 
            />
        </>
    );
}; 