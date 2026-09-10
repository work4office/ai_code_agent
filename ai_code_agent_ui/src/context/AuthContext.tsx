import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { api, setupInterceptors } from '../api/axios';
import type { AuthContextType, UserProfile, LoginResponse, LoginRequest } from '../types/auth.types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Use a mutable ref to access the immediate token value inside interceptor closures
  const accessTokenRef = useRef<string | null>(null);

  const setAuth = (token: string | null, userData: UserProfile | null) => {
    setAccessToken(token);
    accessTokenRef.current = token;
    setUser(userData);
  };

  const refresh = async (): Promise<string> => {
    try {
      // Backend reads HTTP-Only cookie automatically and issues a new access token
      const response = await api.post('/auth/refresh');
      const { access_token: newToken, user: userData } = response.data;
      setAuth(newToken, userData);
      return newToken;
    } catch (error) {
      setAuth(null, null);
      throw error;
    }
  };

  // Wire up the interceptors once during app initialization
  useEffect(() => {
    setupInterceptors(
      () => accessTokenRef.current,
      refresh
    );

    // Run silent refresh on initial load to restore sessions seamlessly
    refresh().finally(() => setIsLoading(false));
  }, []);

  const login = async (credentials: Record<string, string>) => {
    const requestBody = credentials as LoginRequest;
    const response = await api.post('/auth/login', requestBody);
    const { access_token: token, user: userData }: LoginResponse = response.data;
    setAuth(token, userData);
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      setAuth(null, null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, login, logout, isLoading }}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
