import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
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

  useEffect(() => {
    const keycloakInstance = new Keycloak({
      url: process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080',
      realm: process.env.REACT_APP_KEYCLOAK_REALM || 'network-access',
      clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'network-portal',
    });

    keycloakInstance
      .init({ onLoad: 'login-required', checkLoginIframe: false })
      .then((authenticated) => {
        setKeycloak(keycloakInstance);
        setIsAuthenticated(authenticated);
      })
      .catch(() => {
        console.error('Keycloak initialization failed');
      });
  }, []);

  if (!keycloak) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</Box>;
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
