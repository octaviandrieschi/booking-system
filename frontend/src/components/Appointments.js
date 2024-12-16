// Componenta pentru afișarea și gestionarea programărilor utilizatorului
// Permite vizualizarea, anularea și accesarea chitanțelor pentru programări

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Stack,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Snackbar
} from '@mui/material';
import {
  CalendarMonth,
  Receipt as ReceiptIcon,
  Cancel as CancelIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon
} from '@mui/icons-material';

function Appointments() {
  // State-uri pentru gestionarea datelor și UI
  const [appointments, setAppointments] = useState([]); // Lista programărilor
  const [error, setError] = useState(null); // Mesaje de eroare
  const [loading, setLoading] = useState(true); // Indicator încărcare
  const [openDialog, setOpenDialog] = useState(false); // Control dialog anulare
  const [selectedAppointment, setSelectedAppointment] = useState(null); // Programarea selectată pentru anulare
  const [snackbarOpen, setSnackbarOpen] = useState(false); // Control notificare
  const [snackbarMessage, setSnackbarMessage] = useState(''); // Mesaj notificare
  const navigate = useNavigate();

  // Funcție pentru preluarea programărilor de la server
  const fetchAppointments = useCallback(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    fetch('http://localhost:5000/api/appointments/my', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => {
        if (!res.ok) throw new Error('Nu s-au putut încărca programările');
        return res.json();
      })
      .then(data => {
        setAppointments(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [navigate]);

  // Încarcă programările la montarea componentei
  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  // Gestionează click-ul pe butonul de anulare
  const handleCancelClick = (appointment) => {
    setSelectedAppointment(appointment);
    setOpenDialog(true);
  };

  // Gestionează confirmarea anulării programării
  const handleCancelConfirm = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://localhost:5000/api/appointments/${selectedAppointment.id}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Nu s-a putut anula programarea');
      }

      // Actualizează starea programării în interfață
      setAppointments(prevAppointments => 
        prevAppointments.map(apt => 
          apt.id === selectedAppointment.id 
            ? { ...apt, status: 'cancelled' } 
            : apt
        )
      );

      setSnackbarMessage('Programarea a fost anulată cu succes');
      setSnackbarOpen(true);
    } catch (err) {
      setError(err.message);
    }
    setOpenDialog(false);
  };

  // Verifică dacă o programare poate fi anulată (cu cel puțin 24h înainte)
  const canCancelAppointment = (dateTime) => {
    const appointmentDate = new Date(dateTime);
    const now = new Date();
    const twentyFourHoursFromNow = new Date(now.getTime() + (24 * 60 * 60 * 1000));
    return appointmentDate > twentyFourHoursFromNow;
  };

  // Formatează data și ora pentru afișare
  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('ro-RO', { 
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  // Afișează indicator de încărcare
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  // Randarea interfeței cu programări
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Antet cu titlu */}
        <Box display="flex" alignItems="center" mb={2}>
          <CalendarMonth sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
          <Typography variant="h4" component="h1">
            Programările Mele
          </Typography>
        </Box>

        {/* Alertă informativă pentru regula de anulare */}
        <Alert 
          severity="info" 
          icon={<InfoIcon />}
          sx={{ 
            mb: 3,
            backgroundColor: 'info.lighter',
            '& .MuiAlert-icon': {
              color: 'info.main'
            }
          }}
        >
          Programările pot fi anulate doar cu cel puțin 24 de ore înainte de ora stabilită
        </Alert>

        {/* Afișare erori */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Lista de programări sau mesaj când nu există */}
        {appointments.length === 0 ? (
          <Box textAlign="center" py={4}>
            <Typography variant="h6" gutterBottom>
              Nu aveți programări active.
            </Typography>
            <Button
              variant="contained"
              startIcon={<CalendarMonth />}
              onClick={() => navigate('/book')}
              sx={{ mt: 2 }}
            >
              Creează o Programare
            </Button>
          </Box>
        ) : (
          // Grid de carduri cu programări
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            {appointments.map(appointment => (
              <Box key={appointment.id} sx={{ flexBasis: { xs: '100%', sm: 'calc(50% - 24px)', md: 'calc(33.333% - 24px)' } }}>
                <Card sx={{ opacity: appointment.status === 'cancelled' ? 0.8 : 1 }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        {appointment.service_name}
                      </Typography>
                      {appointment.status === 'cancelled' ? (
                        <Chip
                          label="Anulat"
                          color="error"
                          size="small"
                          icon={<CancelIcon />}
                        />
                      ) : !canCancelAppointment(appointment.date_time) && (
                        <Chip
                          label="Nu poate fi anulată"
                          color="warning"
                          size="small"
                          sx={{ fontSize: '0.75rem' }}
                        />
                      )}
                    </Box>
                    <Typography color="textSecondary" gutterBottom>
                      <strong>Data și Ora:</strong>{' '}
                      {formatDateTime(appointment.date_time)}
                    </Typography>
                    <Typography color="textSecondary">
                      <strong>Preț:</strong> {appointment.price} RON
                    </Typography>
                    {!appointment.status && !canCancelAppointment(appointment.date_time) && (
                      <Typography 
                        variant="caption" 
                        color="warning.main" 
                        sx={{ 
                          display: 'block', 
                          mt: 1,
                          fontStyle: 'italic'
                        }}
                      >
                        * Programările pot fi anulate doar cu cel puțin 24 de ore înainte
                      </Typography>
                    )}
                  </CardContent>
                  <CardActions>
                    <Stack direction="row" spacing={1} sx={{ width: '100%', justifyContent: 'flex-end' }}>
                      <Button
                        size="small"
                        startIcon={<ReceiptIcon />}
                        onClick={() => navigate(`/receipt/${appointment.id}`)}
                      >
                        Vezi Chitanța
                      </Button>
                      {appointment.status !== 'cancelled' && canCancelAppointment(appointment.date_time) && (
                        <Button
                          size="small"
                          color="error"
                          startIcon={<CancelIcon />}
                          onClick={() => handleCancelClick(appointment)}
                        >
                          Anulează
                        </Button>
                      )}
                    </Stack>
                  </CardActions>
                </Card>
              </Box>
            ))}
          </Box>
        )}
      </Paper>

      {/* Dialog de confirmare pentru anulare */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          Confirmare Anulare
        </DialogTitle>
        <DialogContent>
          <Typography>
            Sunteți sigur că doriți să anulați această programare?
          </Typography>
          {selectedAppointment && (
            <Box sx={{ mt: 2, bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>Serviciu:</strong> {selectedAppointment.service_name}
              </Typography>
              <Typography variant="body2">
                <strong>Data:</strong> {formatDateTime(selectedAppointment.date_time)}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>
            Nu
          </Button>
          <Button onClick={handleCancelConfirm} color="error" variant="contained">
            Da, Anulează
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notificare pentru acțiuni */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
}

export default Appointments;
