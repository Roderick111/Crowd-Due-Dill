/**
 * auth0Service-compiled.js - Pre-compiled Auth0 Authentication Service
 * Purpose: Handles Auth0 authentication without requiring Babel transpilation
 * This version loads immediately and doesn't depend on React compilation timing
 */

// Auth0 SPA SDK wrapper (pre-compiled, no Babel needed)
window.auth0Client = null;
window.auth0InitPromise = null;
window.auth0InitError = null;
window.auth0Ready = false;

// Wait for Auth0 SDK to be available
async function waitForAuth0SDK() {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 20;
    const checkInterval = 250;
    
    const checkAuth0 = () => {
      attempts++;
      console.log(`🔍 Checking Auth0 SDK availability (attempt ${attempts}/${maxAttempts})...`);
      
      if (typeof auth0 !== 'undefined' && auth0.createAuth0Client) {
        console.log('✅ Auth0 SDK is available');
        resolve(true);
      } else if (attempts >= maxAttempts) {
        const error = new Error(`Auth0 SDK not available after ${maxAttempts} attempts. Please check your internet connection and refresh the page.`);
        console.error('❌ Auth0 SDK timeout:', error);
        reject(error);
      } else {
        console.log(`⏳ Auth0 SDK not ready yet, retrying in ${checkInterval}ms...`);
        setTimeout(checkAuth0, checkInterval);
      }
    };
    
    checkAuth0();
  });
}

async function initAuth0() {
  // Prevent multiple initialization attempts
  if (window.auth0InitPromise) {
    return window.auth0InitPromise;
  }

  console.log('🚀 Starting Auth0 initialization (pre-compiled)...');

  window.auth0InitPromise = (async () => {
    try {
      // Step 1: Wait for Auth0 SDK to be available
      await waitForAuth0SDK();
      
      // Step 2: Validate Auth0 SDK
      if (typeof auth0 === 'undefined') {
        throw new Error('Auth0 global object not found after SDK load');
      }
      
      if (!auth0.createAuth0Client) {
        throw new Error('Auth0.createAuth0Client method not available');
      }

      // Step 3: Configure and create Auth0 client using configuration system
      const auth0Config = window.AppConfig ? window.AppConfig.getAuth0Config() : null;
      
      if (!auth0Config || !auth0Config.domain || !auth0Config.clientId) {
        throw new Error('Auth0 configuration missing. Please ensure secrets.js is loaded with proper credentials.');
      }
      const redirectUri = window.AppConfig ? window.AppConfig.getRedirectUri() : `${window.location.origin}/web/`;

      // Create Auth0 client
      window.auth0Client = await auth0.createAuth0Client({
        domain: auth0Config.domain,
        clientId: auth0Config.clientId,
        audience: auth0Config.audience,
        cacheLocation: 'localstorage',
        useRefreshTokens: true,
        authorizationParams: {
          redirect_uri: redirectUri,
          scope: auth0Config.scope || 'openid profile email',
          audience: auth0Config.audience
        }
      });

      // Step 4: Validate client creation
      if (!window.auth0Client) {
        throw new Error('Auth0 client creation returned null/undefined');
      }

      // Step 5: Handle redirect callback if present
      if (window.location.search.includes('code=') && window.location.search.includes('state=')) {
        console.log('🔄 Processing Auth0 callback...');
        
        try {
          const result = await window.auth0Client.handleRedirectCallback();
          console.log('✅ Auth0 callback processed:', result);
          
          // Clean up URL
          window.history.replaceState({}, document.title, '/web/');
          
          // Refresh page to update auth state
          setTimeout(() => {
            window.location.reload();
          }, 100);
        } catch (callbackError) {
          console.error('❌ Auth0 callback error:', callbackError);
          window.history.replaceState({}, document.title, '/web/');
        }
      }

      // Step 6: Mark as ready
      window.auth0Ready = true;
      console.log('✅ Auth0 initialization completed successfully (pre-compiled)!');
      
      return window.auth0Client;
    } catch (error) {
      console.error('❌ Auth0 initialization failed:', error);
      window.auth0InitError = error;
      window.auth0Ready = false;
      throw error;
    }
  })();

  return window.auth0InitPromise;
}

// Wait for configuration to be available before making initAuth0 available
async function waitForConfiguration() {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 50; // 5 seconds max wait
    const checkInterval = 100;
    
    const checkConfig = () => {
      attempts++;
      console.log(`🔍 Checking configuration availability (attempt ${attempts}/${maxAttempts})...`);
      
      if (window.AppConfig && window.AppSecrets) {
        console.log('✅ Configuration is available');
        resolve(true);
      } else if (attempts >= maxAttempts) {
        const error = new Error(`Configuration not available after ${maxAttempts} attempts. Please ensure config.js and secrets.js are loaded.`);
        console.error('❌ Configuration timeout:', error);
        reject(error);
      } else {
        console.log(`⏳ Configuration not ready yet (AppConfig: ${!!window.AppConfig}, AppSecrets: ${!!window.AppSecrets}), retrying in ${checkInterval}ms...`);
        setTimeout(checkConfig, checkInterval);
      }
    };
    
    checkConfig();
  });
}

// Enhanced initAuth0 that waits for configuration
async function initAuth0Enhanced() {
  console.log('🚀 Starting enhanced Auth0 initialization...');
  
  try {
    // Wait for configuration first
    await waitForConfiguration();
    console.log('✅ Configuration ready, proceeding with Auth0 initialization...');
    
    // Now call the original initAuth0
    return await initAuth0();
  } catch (error) {
    console.error('❌ Enhanced Auth0 initialization failed:', error);
    throw error;
  }
}

// Make enhanced initAuth0 globally available immediately
window.initAuth0 = initAuth0Enhanced;

// Auth0 state getter
window.getAuth0State = async function() {
  try {
    // Wait for initialization if it's in progress
    if (window.auth0InitPromise && !window.auth0Ready) {
      try {
        await window.auth0InitPromise;
      } catch (initError) {
        console.error('❌ Auth0 initialization failed during state check:', initError);
        return { 
          isAuthenticated: false, 
          user: null, 
          accessToken: null, 
          error: initError
        };
      }
    }
    
    if (!window.auth0Client) {
      const error = window.auth0InitError || new Error('Auth0 client not initialized');
      console.error('❌ Auth0 client not available:', error);
      return { 
        isAuthenticated: false, 
        user: null, 
        accessToken: null, 
        error
      };
    }
    
    const isAuthenticated = await window.auth0Client.isAuthenticated();
    
    let user = null;
    let accessToken = null;
    
    if (isAuthenticated) {
      try {
        user = await window.auth0Client.getUser();
        accessToken = await window.auth0Client.getTokenSilently();
      } catch (tokenError) {
        console.warn('⚠️ Failed to get user info or token:', tokenError);
      }
    }
    
    return { isAuthenticated, user, accessToken, error: null };
  } catch (error) {
    console.error('❌ Error getting Auth0 state:', error);
    return { isAuthenticated: false, user: null, accessToken: null, error };
  }
};

// Auth0 login function
window.auth0Login = async function() {
  try {
    console.log('🚀 Starting login process...');
    
    // Wait for initialization if needed
    if (window.auth0InitPromise && !window.auth0Ready) {
      console.log('⏳ Waiting for Auth0 to initialize before login...');
      await window.auth0InitPromise;
    }
    
    if (!window.auth0Client) {
      throw new Error('Auth0 client not initialized. Please refresh the page and try again.');
    }
    
    console.log('🔐 Redirecting to Auth0 login...');
    await window.auth0Client.loginWithRedirect();
  } catch (error) {
    console.error('❌ Login failed:', error);
    throw error;
  }
};

// Auth0 logout function
window.auth0Logout = async function() {
  try {
    console.log('🚀 Starting logout process...');
    
    if (!window.auth0Client) {
      throw new Error('Auth0 client not initialized. Please refresh the page and try again.');
    }
    
    console.log('🔓 Redirecting to Auth0 logout...');
    await window.auth0Client.logout({
      logoutParams: {
        returnTo: window.location.origin + '/web/'
      }
    });
  } catch (error) {
    console.error('❌ Logout failed:', error);
    throw error;
  }
};

console.log('✅ Auth0 service (pre-compiled) loaded and ready'); 