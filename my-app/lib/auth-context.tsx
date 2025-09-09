"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient, User, LoginRequest, RegisterRequest } from './api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateProfile: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  useEffect(() => {
    // Hydrate from localStorage immediately for fast tab reloads/new tabs
    try {
      const stored = typeof window !== 'undefined' ? window.localStorage.getItem('user') : null;
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && parsed.id) setUser(parsed);
      }
    } catch {}

    // Check if token is present and refresh profile
    const checkAuth = async () => {
      if (apiClient.isAuthenticated()) {
        try {
          const response = await apiClient.getProfile();
          setUser(response.user);
          try { if (typeof window !== 'undefined') window.localStorage.setItem('user', JSON.stringify(response.user)); } catch {}
        } catch (error) {
          console.error('Failed to get user profile:', error);
          // Do NOT clear token or broadcast logout across tabs on a transient error.
          // Keep existing localStorage user; only clear local state.
          setUser(prev => prev || null);
        }
      }
      setIsLoading(false);
    };

    checkAuth();

    // Keep tabs in sync (token/user changes across tabs)
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'user') {
        if (e.newValue) {
          try { setUser(JSON.parse(e.newValue)); } catch {}
        } else {
          setUser(null);
        }
      }
    };
    if (typeof window !== 'undefined') window.addEventListener('storage', onStorage);
    return () => { if (typeof window !== 'undefined') window.removeEventListener('storage', onStorage); };
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await apiClient.login(credentials);
      setUser(response.user);
      try { if (typeof window !== 'undefined') window.localStorage.setItem('user', JSON.stringify(response.user)); } catch {}
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData: RegisterRequest) => {
    try {
      const response = await apiClient.register(userData);
      setUser(response.user);
      try { if (typeof window !== 'undefined') window.localStorage.setItem('user', JSON.stringify(response.user)); } catch {}
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
    try { if (typeof window !== 'undefined') window.localStorage.removeItem('user'); } catch {}
  };

  const updateProfile = async (userData: Partial<User>) => {
    try {
      if (!user) {
        throw new Error("User not found");
      }
      const response = await apiClient.updateProfile(userData, user.id);
      setUser(response.user);
      try { if (typeof window !== 'undefined') window.localStorage.setItem('user', JSON.stringify(response.user)); } catch {}
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
