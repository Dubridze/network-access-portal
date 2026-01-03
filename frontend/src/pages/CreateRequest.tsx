import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  SelectChangeEvent,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { apiService } from '../services/api';

const CreateRequest: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    source_ip: '',
    destination_ip: '',
    destination_hostname: '',
    port: '22',
    protocol: 'ssh',
    description: '',
    business_justification: '',
  });
  const [error, setError] = useState<string | null>(null);

  const { mutate: createRequest, isPending } = useMutation({
    mutationFn: (data: any) => apiService.createAccessRequest(data),
    onSuccess: (response: any) => {
      navigate(`/requests/${response.id}`);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create request');
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name as string]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createRequest(formData);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Create New Access Request
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Source IP"
                  name="source_ip"
                  value={formData.source_ip}
                  onChange={handleChange}
                  fullWidth
                  required
                  placeholder="192.168.1.1"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Destination IP"
                  name="destination_ip"
                  value={formData.destination_ip}
                  onChange={handleChange}
                  fullWidth
                  required
                  placeholder="10.0.0.1"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Destination Hostname (Optional)"
                  name="destination_hostname"
                  value={formData.destination_hostname}
                  onChange={handleChange}
                  fullWidth
                  placeholder="server.example.com"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Port"
                  name="port"
                  type="number"
                  value={formData.port}
                  onChange={handleChange}
                  fullWidth
                  inputProps={{ min: '1', max: '65535' }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Protocol</InputLabel>
                  <Select
                    name="protocol"
                    value={formData.protocol}
                    onChange={handleSelectChange}
                    label="Protocol"
                  >
                    <MenuItem value="tcp">TCP</MenuItem>
                    <MenuItem value="udp">UDP</MenuItem>
                    <MenuItem value="ssh">SSH</MenuItem>
                    <MenuItem value="https">HTTPS</MenuItem>
                    <MenuItem value="http">HTTP</MenuItem>
                    <MenuItem value="icmp">ICMP</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  fullWidth
                  multiline
                  rows={3}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Business Justification"
                  name="business_justification"
                  value={formData.business_justification}
                  onChange={handleChange}
                  fullWidth
                  multiline
                  rows={4}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={isPending}
                  >
                    Submit Request
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/requests')}
                  >
                    Cancel
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CreateRequest;
