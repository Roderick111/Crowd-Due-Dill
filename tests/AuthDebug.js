/**
 * AuthDebug.js - Authentication Debug Component (DISABLED)
 * Purpose: Provides debugging information and manual testing for Auth0 integration.
 * Status: DISABLED and moved to tests folder for archival purposes.
 * Note: This component is no longer active in the application.
 */
const AuthDebug = () => {
    const { isAuthenticated, isLoading, user, error } = useAuth();
    const [debugInfo, setDebugInfo] = React.useState(null);
    const [showDebug, setShowDebug] = React.useState(false);

    // DISABLED: AuthDebug component is disabled
    React.useEffect(() => {
        setShowDebug(false); // Always disabled
    }, []);

    const refreshDebugInfo = () => {
        if (window.debugAuth0) {
            setDebugInfo(window.debugAuth0());
        }
    };

    const testLogin = async () => {
        console.log('🧪 Testing manual login...');
        if (window.auth0Login) {
            await window.auth0Login();
        } else {
            console.error('❌ auth0Login not available');
        }
    };

    const testGetState = async () => {
        console.log('🧪 Testing getAuth0State...');
        if (window.getAuth0State) {
            const state = await window.getAuth0State();
            console.log('Auth0 State:', state);
        } else {
            console.error('❌ getAuth0State not available');
        }
    };

    const clearCacheAndReauth = async () => {
        console.log('🧹 Clearing Auth0 cache and forcing re-authentication...');
        if (window.clearAuth0CacheAndReauth) {
            await window.clearAuth0CacheAndReauth();
        } else {
            console.error('❌ clearAuth0CacheAndReauth not available');
            alert('Cache clearing function not available. Please refresh the page and try again.');
        }
    };

    const checkTokenFormat = async () => {
        console.log('🔍 Checking current token format...');
        try {
            if (window.getAuth0State) {
                const state = await window.getAuth0State();
                if (state.accessToken) {
                    const tokenLength = state.accessToken.length;
                    const isJWT = state.accessToken.split('.').length === 3;
                    const tokenType = isJWT ? 'JWT' : 'Opaque';
                    
                    console.log(`🎫 Token format: ${tokenType} (${tokenLength} chars)`);
                    console.log(`🎫 Token preview: ${state.accessToken.substring(0, 50)}...`);
                    
                    if (!isJWT) {
                        console.warn('⚠️ Opaque token detected! Need to clear cache and re-authenticate for JWT tokens.');
                    } else {
                        console.log('✅ JWT token detected! Backend authentication should work.');
                    }
                    
                    alert(`Token format: ${tokenType} (${tokenLength} chars)\n${isJWT ? '✅ JWT - Backend auth should work' : '⚠️ Opaque - Need to clear cache'}`);
                } else {
                    console.log('❌ No access token available');
                    alert('No access token available. Please login first.');
                }
            }
        } catch (error) {
            console.error('❌ Error checking token format:', error);
            alert('Error checking token format: ' + error.message);
        }
    };

    if (!showDebug) return null;

    return (
        <div className="fixed bottom-4 right-4 bg-gray-800 border border-gray-600 rounded-lg p-4 text-xs text-white max-w-sm z-50">
            <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold text-yellow-400">🔐 Auth Debug</h3>
                <button
                    onClick={() => setShowDebug(false)}
                    className="text-gray-400 hover:text-white"
                >
                    ✕
                </button>
            </div>
            
            <div className="space-y-2">
                <div>
                    <strong>Hook State:</strong>
                    <div className="ml-2">
                        <div>Loading: {isLoading ? '✅' : '❌'}</div>
                        <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
                        <div>User: {user ? '✅' : '❌'}</div>
                        <div>Error: {error ? '❌' : '✅'}</div>
                    </div>
                </div>

                {debugInfo && (
                    <div>
                        <strong>Global State:</strong>
                        <div className="ml-2">
                            <div>auth0 global: {debugInfo.auth0Global ? '✅' : '❌'}</div>
                            <div>auth0Client: {debugInfo.auth0Client ? '✅' : '❌'}</div>
                            <div>initPromise: {debugInfo.initPromise ? '✅' : '❌'}</div>
                            <div>initError: {debugInfo.initError ? '❌' : '✅'}</div>
                        </div>
                    </div>
                )}

                <div className="flex flex-wrap gap-1">
                    <button
                        onClick={refreshDebugInfo}
                        className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
                    >
                        Refresh
                    </button>
                    <button
                        onClick={testLogin}
                        className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
                    >
                        Test Login
                    </button>
                    <button
                        onClick={testGetState}
                        className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs"
                    >
                        Test State
                    </button>
                    <button
                        onClick={clearCacheAndReauth}
                        className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                    >
                        Clear Cache & Re-auth
                    </button>
                    <button
                        onClick={checkTokenFormat}
                        className="px-2 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-xs"
                    >
                        Check Token
                    </button>
                </div>

                {error && (
                    <div className="text-red-400 text-xs">
                        <strong>Error:</strong> {error.message}
                    </div>
                )}
            </div>
        </div>
    );
};

// Export for use in other components
window.AuthDebug = AuthDebug; 