/**
 * AuthStatusBanner.js - Authentication Status Banner
 * Purpose: Shows authentication status and benefits to users.
 * Provides contextual information about anonymous vs authenticated usage.
 */
const AuthStatusBanner = () => {
    const { isAuthenticated, user, login } = useAuth();
    const { theme } = useTheme();
    const [isVisible, setIsVisible] = React.useState(true);
    const [isDismissed, setIsDismissed] = React.useState(false);

    // Check if banner was previously dismissed
    React.useEffect(() => {
        const dismissed = localStorage.getItem('auth_banner_dismissed');
        if (dismissed === 'true') {
            setIsDismissed(true);
            setIsVisible(false);
        }
    }, []);

    // Don't show if dismissed or if authenticated
    if (isDismissed || isAuthenticated || !isVisible) {
        return null;
    }

    const handleDismiss = () => {
        localStorage.setItem('auth_banner_dismissed', 'true');
        setIsDismissed(true);
        setIsVisible(false);
    };

    // Dynamic styling based on theme
    const bannerStyles = theme === 'light' 
        ? "bg-gradient-to-r from-blue-100 to-purple-100 border-b border-blue-200"
        : "bg-gradient-to-r from-blue-600/90 to-purple-600/90 border-b border-blue-500/50";
    
    const iconStyles = theme === 'light'
        ? "w-8 h-8 bg-blue-200 rounded-full flex items-center justify-center"
        : "w-8 h-8 bg-white/20 rounded-full flex items-center justify-center";
    
    const iconColor = theme === 'light' ? "text-blue-600" : "text-white";
    
    const textStyles = theme === 'light' ? "text-gray-800" : "text-white";
    const subTextStyles = theme === 'light' ? "text-gray-600" : "text-blue-100";
    
    const buttonStyles = theme === 'light'
        ? "px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        : "px-4 py-2 bg-white text-blue-600 rounded-lg text-sm font-medium hover:bg-blue-50 transition-colors";
    
    const dismissStyles = theme === 'light'
        ? "p-1 text-gray-600 hover:text-gray-800 transition-colors"
        : "p-1 text-white/70 hover:text-white transition-colors";

    return (
        <div className={bannerStyles}>
            <div className="max-w-6xl mx-auto px-4 py-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        {/* Icon */}
                        <div className={iconStyles}>
                            <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>

                        {/* Message */}
                        <div className={textStyles}>
                            <div className="text-sm font-medium">
                                Sign in to save your sessions and preferences
                            </div>
                            <div className={`text-xs ${subTextStyles}`}>
                                Currently using anonymous mode - sessions won't be saved permanently
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={login}
                            className={buttonStyles}
                        >
                            Sign In
                        </button>
                        
                        <button
                            onClick={handleDismiss}
                            className={dismissStyles}
                            title="Dismiss"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}; 