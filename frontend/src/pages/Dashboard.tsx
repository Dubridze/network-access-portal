import { Box, Card, CardContent, Grid, Typography, LinearProgress, Alert, AlertTitle } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const Dashboard: React.FC = () => {
  const { hasRole } = useAuth();

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => apiService.getAdminStats(),
    enabled: hasRole('admin'),
    retry: 1,
  });

  if (isLoading && hasRole('admin')) {
    return <LinearProgress />;
  }

  if (error && hasRole('admin')) {
    console.error('Error loading admin stats:', error);
    return (
      <Alert severity="error">
        <AlertTitle>Failed to Load Statistics</AlertTitle>
        Unable to load admin statistics. Make sure the backend API is running at{' '}
        {process.env.REACT_APP_API_URL || 'http://localhost:8000'}.
        <br />
        <small style={{ marginTop: '8px', display: 'block' }}>
          Error: {error instanceof Error ? error.message : String(error)}
        </small>
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Dashboard
      </Typography>

      {hasRole('admin') && stats && (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Requests
                </Typography>
                <Typography variant="h5">{stats.total_requests || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Pending
                </Typography>
                <Typography variant="h5" sx={{ color: '#ff9800' }}>
                  {stats.pending_requests || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Approved
                </Typography>
                <Typography variant="h5" sx={{ color: '#4caf50' }}>
                  {stats.approved_requests || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Users
                </Typography>
                <Typography variant="h5">{stats.total_users || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {!hasRole('admin') && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Welcome!
            </Typography>
            <Typography color="textSecondary">
              Use the menu to create or manage your network access requests.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Dashboard;
