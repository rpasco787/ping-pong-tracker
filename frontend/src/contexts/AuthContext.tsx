"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, login as apiLogin, register as apiRegister, getCurrentUser, logout as apiLogout, isAuthenticated } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    if (isAuthenticated()) {
      getCurrentUser()
        .then(setUser)
        .catch(() => {
          // Token is invalid, clear it
          apiLogout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    await apiLogin({ username, password });
    const currentUser = await getCurrentUser();
    setUser(currentUser);
  };

  const register = async (username: string, email: string, password: string) => {
    await apiRegister({ username, email, password });
    // After registration, automatically log in
    await login(username, password);
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

