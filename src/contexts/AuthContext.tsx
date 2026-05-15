import React, { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import {
  configureAuthHandlers,
  fetchMe,
  loginRequest,
  SessionTokens,
  setSessionTokens,
} from '../services/api';

type AuthContextType = {
  token: string | null;
  timezoneConfirmed: boolean | null;
  sessionExpiredMessage: string | null;
  signIn(username: string, password: string): Promise<void>;
  signOut(): void;
  consumeSessionExpiredMessage(): void;
  markTimezoneConfirmed(): void;
};

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSessionState] = useState<SessionTokens | null>(null);
  const [timezoneConfirmed, setTimezoneConfirmed] = useState<boolean | null>(null);
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState<string | null>(null);

  const setSession = useCallback((tokens: SessionTokens | null) => {
    setSessionTokens(tokens);
    setSessionState(tokens);
  }, []);

  const handleSessionExpired = useCallback(() => {
    setSession(null);
    setTimezoneConfirmed(null);
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
    setTimezoneConfirmed(null);
    const profile = await fetchMe();
    setTimezoneConfirmed(profile.timezone_confirmed);
  }

  function signOut() {
    setSession(null);
    setTimezoneConfirmed(null);
  }

  function consumeSessionExpiredMessage() {
    setSessionExpiredMessage(null);
  }

  function markTimezoneConfirmed() {
    setTimezoneConfirmed(true);
  }

  const contextValue = useMemo(
    () => ({
      token: session?.accessToken ?? null,
      timezoneConfirmed,
      sessionExpiredMessage,
      signIn,
      signOut,
      consumeSessionExpiredMessage,
      markTimezoneConfirmed,
    }),
    [session, timezoneConfirmed, sessionExpiredMessage],
  );

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}
