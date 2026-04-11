import { createContext, useContext, useMemo, useState } from 'react';
import { api } from '../lib/api';
import { clearAuth, getStoredUser, getToken, setAuth, type AuthUser } from '../lib/auth';

type LoginPayload = { email: string; password: string };
type AuthContextShape = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextShape | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(getToken());
  const [user, setUser] = useState<AuthUser | null>(getStoredUser());

  const value = useMemo<AuthContextShape>(
    () => ({
      user,
      token,
      isAuthenticated: !!token,
      login: async ({ email, password }) => {
        const res = await api.post('/auth/login', { email, password });
        setAuth(res.data.access_token, res.data.user);
        setToken(res.data.access_token);
        setUser(res.data.user);
      },
      logout: () => {
        clearAuth();
        setToken(null);
        setUser(null);
      },
    }),
    [token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
