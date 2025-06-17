/**
 * Frontend Configuration Management
 * Centralizes all environment-specific settings and removes hardcoded values
 */

// Environment detection
const getEnvironment = () => {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // Production environment
    if (hostname === 'crowd-reg.beautiful-apps.com') {
        return 'production';
    }
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'development';
    }
    
    // Default to development for unknown environments
    return 'development';
};

// Configuration object
const config = {
    // Current environment
    environment: getEnvironment(),
    
    // API Configuration
    api: {
        development: {
            baseUrl: 'http://localhost:8000',
            timeout: 30000
        },
        production: {
            baseUrl: 'https://crowd-reg.beautiful-apps.com',
            timeout: 30000
        }
    },
    
    // Auth0 Configuration (get from secrets or environment)
    auth0: {
        development: {
            // These should come from secrets.js or environment variables
            domain: null, // Will be loaded from secrets
            clientId: null, // Will be loaded from secrets
            audience: 'https://crowd-reg-api',
            scope: 'openid profile email'
        },
        production: {
            // These should come from secrets.js or environment variables
            domain: null, // Will be loaded from secrets
            clientId: null, // Will be loaded from secrets
            audience: 'https://crowd-reg-api',
            scope: 'openid profile email'
        }
    },
    
    // Application URLs
    app: {
        development: {
            baseUrl: 'http://localhost:8000',
            redirectUri: 'http://localhost:8000/'
        },
        production: {
            baseUrl: 'https://crowd-reg.beautiful-apps.com',
            redirectUri: 'https://crowd-reg.beautiful-apps.com/'
        }
    },
    
    // Feature flags
    features: {
        development: {
            debugMode: true,
            enableConsoleLogging: true,
            enableMetrics: false
        },
        production: {
            debugMode: false,
            enableConsoleLogging: false,
            enableMetrics: true
        }
    }
};

// Helper functions to get current environment config
const getCurrentConfig = (section) => {
    const env = config.environment;
    let baseConfig = config[section][env] || config[section].development;
    
    // Merge with secrets if available
    if (window.AppSecrets && window.AppSecrets[section]) {
        const secrets = window.AppSecrets[section][env] || window.AppSecrets[section].development;
        baseConfig = { ...baseConfig, ...secrets };
    }
    
    return baseConfig;
};

// Export configuration getters
window.AppConfig = {
    // Environment info
    getEnvironment: () => config.environment,
    isProduction: () => config.environment === 'production',
    isDevelopment: () => config.environment === 'development',
    
    // API configuration
    getApiConfig: () => getCurrentConfig('api'),
    getApiBaseUrl: () => getCurrentConfig('api').baseUrl,
    getApiTimeout: () => getCurrentConfig('api').timeout,
    
    // Auth0 configuration
    getAuth0Config: () => getCurrentConfig('auth0'),
    getAuth0Domain: () => getCurrentConfig('auth0').domain,
    getAuth0ClientId: () => getCurrentConfig('auth0').clientId,
    getAuth0Audience: () => getCurrentConfig('auth0').audience,
    getAuth0Scope: () => getCurrentConfig('auth0').scope,
    
    // App URLs
    getAppConfig: () => getCurrentConfig('app'),
    getAppBaseUrl: () => getCurrentConfig('app').baseUrl,
    getRedirectUri: () => getCurrentConfig('app').redirectUri,
    
    // Features
    getFeatures: () => getCurrentConfig('features'),
    isDebugMode: () => getCurrentConfig('features').debugMode,
    isConsoleLoggingEnabled: () => getCurrentConfig('features').enableConsoleLogging,
    isMetricsEnabled: () => getCurrentConfig('features').enableMetrics,
    
    // Utility method to get all config for debugging
    getFullConfig: () => config
};

// Console logging helper that respects environment
window.AppConfig.log = (...args) => {
    if (window.AppConfig.isConsoleLoggingEnabled()) {
        console.log(...args);
    }
};

window.AppConfig.warn = (...args) => {
    if (window.AppConfig.isConsoleLoggingEnabled()) {
        console.warn(...args);
    }
};

window.AppConfig.error = (...args) => {
    // Always log errors regardless of environment
    console.error(...args);
};

// Initialize and log current configuration
window.AppConfig.log('🔧 Frontend Configuration Initialized');
window.AppConfig.log('Environment:', window.AppConfig.getEnvironment());
window.AppConfig.log('API Base URL:', window.AppConfig.getApiBaseUrl());
window.AppConfig.log('Auth0 Domain:', window.AppConfig.getAuth0Domain());
window.AppConfig.log('Redirect URI:', window.AppConfig.getRedirectUri());

// Make config available globally for debugging
if (window.AppConfig.isDebugMode()) {
    window.debugConfig = () => {
        console.table({
            Environment: window.AppConfig.getEnvironment(),
            'API Base URL': window.AppConfig.getApiBaseUrl(),
            'Auth0 Domain': window.AppConfig.getAuth0Domain(),
            'Auth0 Client ID': window.AppConfig.getAuth0ClientId(),
            'Redirect URI': window.AppConfig.getRedirectUri(),
            'Debug Mode': window.AppConfig.isDebugMode(),
            'Console Logging': window.AppConfig.isConsoleLoggingEnabled()
        });
        return window.AppConfig.getFullConfig();
    };
    
    console.log('🐛 Debug mode enabled. Run debugConfig() to see full configuration.');
} 