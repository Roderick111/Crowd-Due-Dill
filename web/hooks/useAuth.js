/**
 * useAuth.js - Authentication State Hook
 * Purpose: Provides authentication state and methods to React components.
 * Manages Auth0 state changes and provides login/logout functionality.
 */
const { useState, useEffect } = React;

// Global auth state manager to prevent multiple simultaneous calls
window.authStateManager = window.authStateManager || {
    currentState: {
        isAuthenticated: false,
        isLoading: true,
        user: null,
        error: null,
        accessToken: null
    },
    lastCheck: 0,
    checkInProgress: false,
    subscribers: new Set(),
    cacheTimeout: 30000, // 30 seconds cache
    
    // Subscribe to auth state changes
    subscribe(callback) {
        this.subscribers.add(callback);
        // Immediately call with current state
        callback(this.currentState);
        
        return () => {
            this.subscribers.delete(callback);
        };
    },
    
    // Notify all subscribers of state change
    notifySubscribers() {
        this.subscribers.forEach(callback => {
            try {
                callback(this.currentState);
            } catch (error) {
                console.error('❌ Auth state subscriber error:', error);
            }
        });
    },
    
    // Check if we need to refresh auth state
    needsRefresh() {
        const now = Date.now();
        return (now - this.lastCheck) > this.cacheTimeout;
    },
    
    // Get auth state with caching
    async getAuthState(forceRefresh = false) {
        // Return cached state if recent and not forcing refresh
        if (!forceRefresh && !this.needsRefresh() && !this.currentState.isLoading) {
            return this.currentState;
        }
        
        // Prevent multiple simultaneous checks
        if (this.checkInProgress) {
            // Wait for current check to complete
            while (this.checkInProgress) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            return this.currentState;
        }
        
        this.checkInProgress = true;
        
        try {
            // Wait for Auth0 to be ready
            if (!window.auth0Ready && window.initAuth0) {
                await window.initAuth0();
            }
            
            if (window.getAuth0State) {
                const state = await window.getAuth0State();
                
                this.currentState = {
                    isAuthenticated: state.isAuthenticated,
                    isLoading: false,
                    user: state.user,
                    error: state.error,
                    accessToken: state.accessToken
                };
                
                this.lastCheck = Date.now();
                this.notifySubscribers();
                
                return this.currentState;
            } else {
                throw new Error('Auth0 state function not available');
            }
        } catch (error) {
            console.error('❌ Auth state check failed:', error);
            
            this.currentState = {
                isAuthenticated: false,
                isLoading: false,
                user: null,
                error,
                accessToken: null
            };
            
            this.notifySubscribers();
            return this.currentState;
        } finally {
            this.checkInProgress = false;
        }
    },
    
    // Force refresh auth state
    async refreshAuthState() {
        return this.getAuthState(true);
    }
};

const useAuth = () => {
    const [authState, setAuthState] = useState(window.authStateManager.currentState);

    useEffect(() => {
        // Subscribe to auth state changes
        const unsubscribe = window.authStateManager.subscribe(setAuthState);
        
        // Initial auth check (will use cache if available)
        window.authStateManager.getAuthState();
        
        return unsubscribe;
    }, []);

    // Authentication methods with improved error handling
    const login = async () => {
        try {
            if (window.auth0Login) {
                await window.auth0Login();
                // Refresh auth state after login
                setTimeout(() => {
                    window.authStateManager.refreshAuthState();
                }, 1000);
            } else {
                throw new Error('Auth0 login function not available');
            }
        } catch (error) {
            console.error('❌ useAuth: Login failed:', error);
            
            // Update state to show error
            window.authStateManager.currentState.error = error;
            window.authStateManager.notifySubscribers();
            
            // Show user-friendly error
            let userMessage = 'Login failed. ';
            if (error.message.includes('not available')) {
                userMessage += 'Please refresh the page and try again.';
            } else if (error.message.includes('network') || error.message.includes('fetch')) {
                userMessage += 'Please check your internet connection.';
            } else {
                userMessage += 'Please try again or contact support if the issue persists.';
            }
            
            alert(userMessage);
        }
    };

    const logout = async () => {
        try {
            if (window.auth0Logout) {
                await window.auth0Logout();
                // Refresh auth state after logout
                setTimeout(() => {
                    window.authStateManager.refreshAuthState();
                }, 1000);
            } else {
                throw new Error('Auth0 logout function not available');
            }
        } catch (error) {
            console.error('❌ useAuth: Logout failed:', error);
            
            // Update state to show error
            window.authStateManager.currentState.error = error;
            window.authStateManager.notifySubscribers();
            
            // Show user-friendly error
            let userMessage = 'Logout failed. ';
            if (error.message.includes('not available')) {
                userMessage += 'Please refresh the page and try again.';
            } else {
                userMessage += 'Please try again or contact support if the issue persists.';
            }
            
            alert(userMessage);
        }
    };

    const getAccessToken = async () => {
        try {
            const state = await window.authStateManager.getAuthState();
            return state.accessToken;
        } catch (error) {
            console.error('❌ useAuth: Failed to get access token:', error);
            return null;
        }
    };

    // Refresh auth state (useful after login/logout)
    const refreshAuth = async () => {
        try {
            await window.authStateManager.refreshAuthState();
        } catch (error) {
            console.error('❌ useAuth: Auth refresh failed:', error);
        }
    };

    // Clear error state
    const clearError = () => {
        window.authStateManager.currentState.error = null;
        window.authStateManager.notifySubscribers();
    };

    return {
        ...authState,
        login,
        logout,
        getAccessToken,
        refreshAuth,
        clearError
    };
};

// Export for use in other components
window.useAuth = useAuth; 