import { createContext, useContext, ReactNode } from 'react';
import type Keycloak from 'keycloak-js';

interface AuthContextType {
  keycloak: Keycloak.KeycloakInstance;
  isAuthenticated: boolean;
  user: any;
  hasRole: (role: string) => boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
  keycloak: Keycloak.KeycloakInstance;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children, keycloak }) => {
  const hasRole = (role: string): boolean => {
    const roles = keycloak.tokenParsed?.['roles'] || [];
    return roles.includes(role) || roles.includes(`realm:${role}`);
  };

  const logout = () => {
    keycloak.logout({ redirectUri: window.location.origin });
  };

  const value: AuthContextType = {
    keycloak,
    isAuthenticated: keycloak.authenticated || false,
    user: keycloak.tokenParsed || {},
    hasRole,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
