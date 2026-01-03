import React from 'react';
import { Box, Card, CardContent, Grid, Typography, LinearProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const Dashboard: React.FC = () => {
  const { hasRole } = useAuth();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => apiService.getAdminStats(),
    enabled: hasRole('admin'),
  });

  if (isLoading && hasRole('admin')) {
    return <LinearProgress />;
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
                <Typography variant="h5">{stats.total_requests}</Typography>
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
                  {stats.pending_requests}
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
                  {stats.approved_requests}
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
                <Typography variant="h5">{stats.total_users}</Typography>
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
