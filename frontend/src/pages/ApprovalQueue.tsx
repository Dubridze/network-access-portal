import React from 'react';
import { Box, Typography, Card, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const ApprovalQueue: React.FC = () => {
  const navigate = useNavigate();
  const { data: results, isLoading } = useQuery({
    queryKey: ['pending-requests'],
    queryFn: () => apiService.getAccessRequests({ status: 'pending_approval' }),
  });

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Approval Queue
      </Typography>

      <TableContainer component={Card}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell>Request #</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Source IP</TableCell>
              <TableCell>Destination</TableCell>
              <TableCell>Port</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">Loading...</TableCell>
              </TableRow>
            ) : (results?.requests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">No pending requests</TableCell>
              </TableRow>
            ) : (
              results?.requests.map((request) => (
                <TableRow key={request.id}>
                  <TableCell>{request.request_number}</TableCell>
                  <TableCell>{request.user.username}</TableCell>
                  <TableCell>{request.source_ip}</TableCell>
                  <TableCell>{request.destination_hostname || request.destination_ip}</TableCell>
                  <TableCell>{request.port}</TableCell>
                  <TableCell>{new Date(request.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => navigate(`/requests/${request.id}`)}
                    >
                      Review
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ApprovalQueue;
