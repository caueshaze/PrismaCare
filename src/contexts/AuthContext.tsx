import React, { createContext, useState } from 'react';
import { loginRequest, setToken } from '../services/api';

type AuthContextType = {
  token: string | null;
  signIn(username: string, password: string): Promise<void>;
  signOut(): void;
};

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);

  async function signIn(username: string, password: string) {
    const { access_token } = await loginRequest(username, password);
    setToken(access_token);
    setTokenState(access_token);
  }

  function signOut() {
    setToken(null);
    setTokenState(null);
  }

  return (
    <AuthContext.Provider value={{ token, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
