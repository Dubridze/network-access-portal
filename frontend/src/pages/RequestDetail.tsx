import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Dialog,
  TextField,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const RequestDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogComment, setDialogComment] = useState('');
  const [dialogReason, setDialogReason] = useState('');
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);

  const { data: request, isLoading, refetch } = useQuery({
    queryKey: ['access-request', id],
    queryFn: () => apiService.getAccessRequest(parseInt(id!)),
  });

  const { mutate: approve, isPending: isApproving } = useMutation({
    mutationFn: () => apiService.approveAccessRequest(parseInt(id!), dialogComment),
    onSuccess: () => {
      refetch();
      setOpenDialog(false);
      setDialogComment('');
    },
  });

  const { mutate: reject, isPending: isRejecting } = useMutation({
    mutationFn: () => apiService.rejectAccessRequest(parseInt(id!), dialogReason),
    onSuccess: () => {
      refetch();
      setOpenDialog(false);
      setDialogReason('');
    },
  });

  const handleApprove = () => {
    setActionType('approve');
    setOpenDialog(true);
  };

  const handleReject = () => {
    setActionType('reject');
    setOpenDialog(true);
  };

  const handleDialogSubmit = () => {
    if (actionType === 'approve') {
      approve();
    } else if (actionType === 'reject') {
      reject();
    }
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      created: 'default',
      pending_approval: 'warning',
      approved: 'success',
      rejected: 'error',
    };
    return colors[status] || 'default';
  };

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  if (!request) {
    return <Alert severity="error">Request not found</Alert>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Request {request.request_number}</Typography>
        <Button variant="outlined" onClick={() => navigate('/requests')}>
          Back
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Status</Typography>
                <Chip
                  label={request.status.replace('_', ' ').toUpperCase()}
                  color={getStatusColor(request.status) as any}
                />
              </Box>
              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Source IP
                  </Typography>
                  <Typography variant="body1">{request.source_ip}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Destination IP
                  </Typography>
                  <Typography variant="body1">{request.destination_ip}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Port
                  </Typography>
                  <Typography variant="body1">{request.port}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="textSecondary">
                    Protocol
                  </Typography>
                  <Typography variant="body1">{request.protocol.toUpperCase()}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Description
                  </Typography>
                  <Typography variant="body1">{request.description}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Business Justification
                  </Typography>
                  <Typography variant="body1">{request.business_justification}</Typography>
                </Grid>
              </Grid>

              {hasRole('approver') && request.status === 'created' && (
                <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handleApprove}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={handleReject}
                  >
                    Reject
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {actionType === 'approve' ? 'Approve Request' : 'Reject Request'}
          </Typography>
          {actionType === 'approve' ? (
            <TextField
              fullWidth
              label="Comment (Optional)"
              value={dialogComment}
              onChange={(e) => setDialogComment(e.target.value)}
              multiline
              rows={3}
            />
          ) : (
            <TextField
              fullWidth
              label="Rejection Reason"
              value={dialogReason}
              onChange={(e) => setDialogReason(e.target.value)}
              multiline
              rows={3}
              required
            />
          )}
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button
              variant="contained"
              color={actionType === 'approve' ? 'success' : 'error'}
              onClick={handleDialogSubmit}
              disabled={isApproving || isRejecting || (actionType === 'reject' && !dialogReason)}
            >
              {actionType === 'approve' ? 'Approve' : 'Reject'}
            </Button>
            <Button variant="outlined" onClick={() => setOpenDialog(false)}>
              Cancel
            </Button>
          </Box>
        </Box>
      </Dialog>
    </Box>
  );
};

export default RequestDetail;
