/**
 * apiService.js - Backend Communication Layer
 * Purpose: Centralized HTTP client for all API calls with unified error handling.
 * Single source of truth for backend communication and request/response processing.
 * Context7 Compliant: Follows modern fetch API patterns and error handling best practices.
 */

// Context7 Best Practice: Custom Error Classes for Better Error Handling
class ApiError extends Error {
    constructor(response, message) {
        super(message || `HTTP ${response.status}: ${response.statusText}`);
        this.name = 'ApiError';
        this.response = response;
        this.status = response.status;
        this.statusText = response.statusText;
    }
}

class NetworkError extends Error {
    constructor(originalError) {
        super(`Network error: ${originalError.message}`);
        this.name = 'NetworkError';
        this.originalError = originalError;
    }
}

class ApiService {
    constructor(baseUrl = null) {
        // Use configuration system instead of hardcoded URL
        this.baseUrl = baseUrl || (window.AppConfig ? window.AppConfig.getApiBaseUrl() : 'https://localhost:8001');
        // Context7 Best Practice: Cache auth headers to avoid repeated async calls
        this._authHeadersCache = null;
        this._authHeadersCacheTime = 0;
        this._authHeadersCacheTTL = 30000; // 30 seconds
    }

    // Context7 Best Practice: Centralized auth header management with caching
    async _getAuthHeaders() {
        const now = Date.now();
        
        // Return cached headers if still valid
        if (this._authHeadersCache && (now - this._authHeadersCacheTime) < this._authHeadersCacheTTL) {
            return this._authHeadersCache;
        }

        let authHeaders = {};
        
        try {
            // Use the new auth state manager for better caching and reliability
            if (window.authStateManager) {
                const authState = await window.authStateManager.getAuthState();
                if (authState.isAuthenticated && authState.accessToken) {
                    // Context7 Best Practice: Validate token format
                    const token = authState.accessToken;
                    const isJWT = token.split('.').length === 3;
                    
                    if (!isJWT) {
                        console.warn('⚠️ Received opaque token instead of JWT. Please clear Auth0 cache and re-authenticate.');
                    }
                    
                    authHeaders = {
                        'Authorization': `Bearer ${authState.accessToken}`
                    };
                    console.log('✅ Auth headers created successfully');
                }
            } else if (window.getAuth0State) {
                // Fallback to direct Auth0 state if manager not available
                const authState = await window.getAuth0State();
                if (authState.isAuthenticated && authState.accessToken) {
                    authHeaders = {
                        'Authorization': `Bearer ${authState.accessToken}`
                    };
                    console.log('✅ Auth headers created successfully (fallback)');
                }
            }
        } catch (authError) {
            // Context7 Best Practice: Only log auth-specific errors, don't throw
            console.warn('⚠️ Could not get auth headers:', authError.message);
        }

        // Cache the headers
        this._authHeadersCache = authHeaders;
        this._authHeadersCacheTime = now;
        
        return authHeaders;
    }

    // Context7 Best Practice: Clear auth cache when needed
    _clearAuthCache() {
        this._authHeadersCache = null;
        this._authHeadersCacheTime = 0;
    }

    // Context7 Best Practice: Centralized request method with proper error handling
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // Get auth headers with caching
        const authHeaders = await this._getAuthHeaders();
        
        // DEBUG: Log header merging for Stripe requests
        if (endpoint.includes('stripe')) {
            console.log('🔍 DEBUG makeRequest for Stripe:');
            console.log('  endpoint:', endpoint);
            console.log('  authHeaders:', authHeaders);
            console.log('  options.headers:', options.headers);
        }
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...authHeaders,
                ...options.headers
            }
        };
        
        // DEBUG: Log final headers for Stripe requests
        if (endpoint.includes('stripe')) {
            console.log('  final config.headers:', config.headers);
            console.log('  has Authorization:', !!config.headers.Authorization);
        }

        let response;
        
        try {
            // Context7 Best Practice: Use fetch with proper error handling
            response = await fetch(url, config);
        } catch (fetchError) {
            // Context7 Best Practice: Wrap network errors in custom error class
            throw new NetworkError(fetchError);
        }
        
        // Context7 Best Practice: Check response.ok for HTTP status validation
        if (!response.ok) {
            // Clear auth cache on 401 errors
            if (response.status === 401) {
                this._clearAuthCache();
            }
            
            let errorMessage;
            
            try {
                // Context7 Best Practice: Try to parse error response as JSON
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`;
            } catch (parseError) {
                // If JSON parsing fails, use status information
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }
            
            console.error(`❌ HTTP ${response.status} error:`, errorMessage);
            throw new ApiError(response, errorMessage);
        }
        
        // Context7 Best Practice: Parse JSON response with error handling
        try {
            return await response.json();
        } catch (parseError) {
            console.warn('⚠️ Response is not valid JSON, returning text');
            return await response.text();
        }
    }

    // Context7 Best Practice: Helper method for cache-busting requests
    _addCacheBuster(endpoint) {
        const separator = endpoint.includes('?') ? '&' : '?';
        return `${endpoint}${separator}_t=${Date.now()}`;
    }

    // Context7 Best Practice: Helper method for no-cache headers
    _getNoCacheHeaders() {
        return {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        };
    }

    // System Status API
    async fetchSystemStatus() {
        try {
            return await this.makeRequest('/status');
        } catch (error) {
            console.error('Error fetching system status:', error);
            throw error;
        }
    }

    // Sessions API - Context7 Best Practice: Consistent cache-busting pattern
    async fetchSessions() {
        try {
            return await this.makeRequest(this._addCacheBuster('/sessions'), {
                headers: this._getNoCacheHeaders()
            });
        } catch (error) {
            console.error('Error fetching sessions:', error);
            throw error;
        }
    }

    async loadSessionMessages(sessionId) {
        try {
            return await this.makeRequest(this._addCacheBuster(`/sessions/${sessionId}/history`), {
                headers: this._getNoCacheHeaders()
            });
        } catch (error) {
            console.error(`Error loading session messages for ${sessionId}:`, error);
            throw error;
        }
    }

    async updateSessionTitle(sessionId, title) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/title`, {
                method: 'PUT',
                body: JSON.stringify({ title })
            });
        } catch (error) {
            console.error('Error updating session title:', error);
            throw error;
        }
    }

    async archiveSession(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/archive`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error archiving session:', error);
            throw error;
        }
    }

    async deleteSession(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Error deleting session:', error);
            throw error;
        }
    }

    async fetchArchivedSessions() {
        try {
            return await this.makeRequest(this._addCacheBuster('/sessions/archived'), {
                headers: this._getNoCacheHeaders()
            });
        } catch (error) {
            console.error('Error fetching archived sessions:', error);
            throw error;
        }
    }

    async unarchiveSession(sessionId) {
        try {
            return await this.makeRequest(`/sessions/${sessionId}/unarchive`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Error unarchiving session:', error);
            throw error;
        }
    }

    // Chat API
    async sendMessage(message, sessionId = null) {
        try {
            return await this.makeRequest('/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }





    // Auth0 API
    async fetchAuthStatus() {
        try {
            return await this.makeRequest('/auth/status');
        } catch (error) {
            console.error('Error fetching auth status:', error);
            throw error;
        }
    }

    async fetchUserInfo() {
        try {
            return await this.makeRequest('/auth/user');
        } catch (error) {
            console.error('Error fetching user info:', error);
            throw error;
        }
    }

    async fetchUserPreferences() {
        try {
            return await this.makeRequest('/auth/user/preferences');
        } catch (error) {
            console.error('Error fetching user preferences:', error);
            throw error;
        }
    }

    async updateUserPreferences(preferences) {
        try {
            return await this.makeRequest('/auth/user/preferences', {
                method: 'POST',
                body: JSON.stringify(preferences)
            });
        } catch (error) {
            console.error('Error updating user preferences:', error);
            throw error;
        }
    }

    async fetchUserSessions() {
        try {
            return await this.makeRequest('/auth/user/sessions');
        } catch (error) {
            console.error('Error fetching user sessions:', error);
            throw error;
        }
    }

    // Context7 Best Practice: Utility method for handling specific error types
    isNetworkError(error) {
        return error instanceof NetworkError;
    }

    isApiError(error) {
        return error instanceof ApiError;
    }

    isAuthError(error) {
        return error instanceof ApiError && error.status === 401;
    }

    // Context7 Best Practice: Method to retry requests with exponential backoff
    async retryRequest(requestFn, maxRetries = 3, baseDelay = 1000) {
        let lastError;
        
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                return await requestFn();
            } catch (error) {
                lastError = error;
                
                // Don't retry on auth errors or client errors (4xx)
                if (this.isAuthError(error) || (this.isApiError(error) && error.status >= 400 && error.status < 500)) {
                    throw error;
                }
                
                // Don't retry on the last attempt
                if (attempt === maxRetries) {
                    break;
                }
                
                // Exponential backoff with jitter
                const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
                console.log(`⏳ Retrying request in ${Math.round(delay)}ms (attempt ${attempt + 1}/${maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        
        throw lastError;
    }
}

// Create a default instance for easy importing
const apiService = new ApiService();

// Export both the class and the default instance
window.ApiService = ApiService;
window.apiService = apiService;
window.ApiError = ApiError;
window.NetworkError = NetworkError; 