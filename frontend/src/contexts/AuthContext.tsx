import { createContext, useContext, useCallback, useMemo, type ReactNode } from "react";

interface AuthContextValue {
  user: null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const login = useCallback(async (_email: string, _password: string) => {}, []);
  const logout = useCallback(async () => {}, []);
  const register = useCallback(async (_email: string, _password: string) => {}, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user: null, login, logout, register }),
    [login, logout, register],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
