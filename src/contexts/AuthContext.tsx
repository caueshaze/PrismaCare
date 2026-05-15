import React, { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import {
  configureAuthHandlers,
  loginRequest,
  SessionTokens,
  setSessionTokens,
} from '../services/api';

type AuthContextType = {
  token: string | null;
  sessionExpiredMessage: string | null;
  signIn(username: string, password: string): Promise<void>;
  signOut(): void;
  consumeSessionExpiredMessage(): void;
};

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSessionState] = useState<SessionTokens | null>(null);
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState<string | null>(null);

  const setSession = useCallback((tokens: SessionTokens | null) => {
    setSessionTokens(tokens);
    setSessionState(tokens);
  }, []);

  const handleSessionExpired = useCallback(() => {
    setSession(null);
    setSessionExpiredMessage('Sua sessão expirou. Entre novamente para continuar.');
  }, [setSession]);

  useEffect(() => {
    configureAuthHandlers({
      onSessionUpdate: setSession,
      onSessionExpired: handleSessionExpired,
    });
  }, [handleSessionExpired, setSession]);

  async function signIn(username: string, password: string) {
    const payload = await loginRequest(username, password);
    setSession({
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
    });
    setSessionExpiredMessage(null);
  }

  function signOut() {
    setSession(null);
  }

  function consumeSessionExpiredMessage() {
    setSessionExpiredMessage(null);
  }

  const contextValue = useMemo(
    () => ({
      token: session?.accessToken ?? null,
      sessionExpiredMessage,
      signIn,
      signOut,
      consumeSessionExpiredMessage,
    }),
    [session, sessionExpiredMessage],
  );

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}
