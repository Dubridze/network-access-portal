import { useState } from 'react';
import { Box, Card, CardContent, Button, Typography, Container, CircularProgress } from '@mui/material';
import { useAuth } from '../context/AuthContext';

const Login: React.FC = () => {
  const { keycloak } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = () => {
    setIsLoading(true);
    keycloak.login();
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Card sx={{ width: '100%', maxWidth: '400px' }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
              Network Access Portal
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
              Please log in to manage your network access requests
            </Typography>
            <Button
              variant="contained"
              color="primary"
              size="large"
              fullWidth
              onClick={handleLogin}
              disabled={isLoading}
              sx={{ py: 1.5 }}
            >
              {isLoading ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Logging in...
                </>
              ) : (
                'Login with Keycloak'
              )}
            </Button>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Login;
