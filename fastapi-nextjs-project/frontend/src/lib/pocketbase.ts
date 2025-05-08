import PocketBase from 'pocketbase';

// Create a single PocketBase instance for the entire app
let pb: PocketBase | null = null;

// Initialize PocketBase
export const initPocketBase = () => {
  if (!pb) {
    // Use environment variable for PocketBase URL or default to localhost
    const pocketbaseUrl = process.env.NEXT_PUBLIC_POCKETBASE_URL || 'http://localhost:8090';
    pb = new PocketBase(pocketbaseUrl);
    
    // Load auth data from localStorage when in browser environment
    if (typeof window !== 'undefined') {
      // Check if we have stored credentials
      const authData = localStorage.getItem('pocketbase_auth');
      if (authData) {
        try {
          const parsedData = JSON.parse(authData);
          pb.authStore.save(parsedData.token, parsedData.model);
        } catch (error) {
          console.error('Error loading stored auth data:', error);
          localStorage.removeItem('pocketbase_auth');
        }
      }
      
      // Subscribe to authStore changes to persist auth state
      pb.authStore.onChange((token, model) => {
        if (token && model) {
          localStorage.setItem('pocketbase_auth', JSON.stringify({
            token,
            model
          }));
        } else {
          localStorage.removeItem('pocketbase_auth');
        }
      });
    }
  }
  
  return pb;
};

// Get the PocketBase instance
export const getPocketBase = () => {
  if (!pb) {
    return initPocketBase();
  }
  return pb;
};

// Authentication helpers
export const isAuthenticated = () => {
  const pb = getPocketBase();
  return pb.authStore.isValid;
};

export const getCurrentUser = () => {
  const pb = getPocketBase();
  return pb.authStore.model;
};

export const login = async (email: string, password: string) => {
  const pb = getPocketBase();
  return await pb.collection('users').authWithPassword(email, password);
};

export const logout = () => {
  const pb = getPocketBase();
  pb.authStore.clear();
};

export const register = async (email: string, password: string, passwordConfirm: string, name: string) => {
  const pb = getPocketBase();
  return await pb.collection('users').create({
    email,
    password,
    passwordConfirm,
    name
  });
};

// Export the PocketBase instance for direct use
export default getPocketBase();
