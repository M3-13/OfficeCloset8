import { createContext, useContext } from 'react';

interface AuthContextType {
  user: null;
  login: (_email: string, _password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (_email: string, _password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: async () => {},
  logout: async () => {},
  register: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const value: AuthContextType = {
    user: null,
    login: async () => {},
    logout: async () => {},
    register: async () => {},
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
