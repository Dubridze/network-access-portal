import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Keycloak from 'keycloak-js';
import type { KeycloakInstance } from 'keycloak-js';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreateRequest from './pages/CreateRequest';
import RequestList from './pages/RequestList';
import RequestDetail from './pages/RequestDetail';
import ApprovalQueue from './pages/ApprovalQueue';
import AuditLog from './pages/AuditLog';
import AdminPanel from './pages/AdminPanel';
import Login from './pages/Login';
import { AuthProvider } from './context/AuthContext';
import { setKeycloakInstance } from './services/api';

const queryClient = new QueryClient();

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#fafafa',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  const [keycloak, setKeycloak] = useState<KeycloakInstance | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const initializeKeycloak = async () => {
      try {
        setIsInitializing(true);
        const keycloakInstance = new Keycloak({
          url: process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080',
          realm: process.env.REACT_APP_KEYCLOAK_REALM || 'network-access',
          clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'network-portal',
        });

        console.log('Initializing Keycloak with:', {
          url: process.env.REACT_APP_KEYCLOAK_URL,
          realm: process.env.REACT_APP_KEYCLOAK_REALM,
          clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID,
        });

        // Use PKCE flow for public clients
        // Code exchange is handled by backend proxy endpoint for security
        const authenticated = await keycloakInstance.init({
          onLoad: 'login-required',
          checkLoginIframe: false,
          pkceMethod: 'S256', // PKCE protocol for public clients
          enableLogging: process.env.NODE_ENV === 'development',
        });

        console.log('Keycloak initialization successful, authenticated:', authenticated);
        
        // Initialize API service with Keycloak instance
        setKeycloakInstance(keycloakInstance);
        
        setKeycloak(keycloakInstance);
        setIsAuthenticated(authenticated);
        setInitError(null);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error('Keycloak initialization failed:', error);
        setInitError(`Authentication initialization failed: ${errorMessage}. Please ensure Keycloak is running at ${process.env.REACT_APP_KEYCLOAK_URL}`);
        setKeycloak(null);
        setIsAuthenticated(false);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeKeycloak();
  }, []);

  if (isInitializing) {
    return (
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#fafafa',
      }}>
        <Box sx={{ textAlign: 'center' }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #1976d2',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px',
          }} />
          <p>Loading...</p>
        </Box>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </Box>
    );
  }

  if (initError) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          padding: 2,
          backgroundColor: '#fafafa',
        }}>
          <Alert severity="error" sx={{ maxWidth: 600 }}>
            <AlertTitle>Authentication Error</AlertTitle>
            {initError}
            <br /><br />
            <strong>Troubleshooting steps:</strong>
            <ul>
              <li>Make sure Keycloak is running</li>
              <li>Check that REACT_APP_KEYCLOAK_URL is correct</li>
              <li>Check browser console for detailed error messages</li>
              <li>Try refreshing the page</li>
            </ul>
          </Alert>
        </Box>
      </ThemeProvider>
    );
  }

  if (!keycloak) {
    return (
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
      }}>
        <p>Keycloak initialization failed</p>
      </Box>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider keycloak={keycloak}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/*"
                element={
                  isAuthenticated ? (
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/requests/new" element={<CreateRequest />} />
                        <Route path="/requests" element={<RequestList />} />
                        <Route path="/requests/:id" element={<RequestDetail />} />
                        <Route path="/approvals" element={<ApprovalQueue />} />
                        <Route path="/audit" element={<AuditLog />} />
                        <Route path="/admin" element={<AdminPanel />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                      </Routes>
                    </Layout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
            </Routes>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
