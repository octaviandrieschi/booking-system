// Componenta pentru gestionarea programului de funcționare
// Permite administratorilor să seteze orele de funcționare și intervalele de programare

import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Box,
  Grid
} from '@mui/material';
import { Save } from '@mui/icons-material';

function BusinessHours() {
  // State-uri pentru gestionarea datelor și UI
  const [hours, setHours] = useState({
    start_time: '09:00',    // Ora de început implicită
    end_time: '17:00',      // Ora de sfârșit implicită
    interval: '30'          // Intervalul implicit între programări (în minute)
  });
  const [error, setError] = useState('');    // Mesaje de eroare
  const [success, setSuccess] = useState(''); // Mesaje de succes

  // Efect pentru încărcarea programului curent la montarea componentei
  useEffect(() => {
    const fetchBusinessHours = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        const response = await fetch(`${apiUrl}/api/business-hours`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch business hours');
        }
        
        const data = await response.json();
        setHours(data);
      } catch (error) {
        console.error('Error:', error);
        setError('Nu s-au putut încărca orele de funcționare');
      }
    };

    fetchBusinessHours();
  }, []);

  // Gestionează trimiterea formularului pentru actualizarea programului
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/business-hours`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(hours)
      });

      if (!response.ok) {
        throw new Error('Failed to update business hours');
      }

      setSuccess('Orele de funcționare au fost actualizate cu succes!');
      setError('');
    } catch (error) {
      console.error('Error:', error);
      setError('Nu s-au putut actualiza orele de funcționare');
      setSuccess('');
    }
  };

  // Randarea interfeței pentru setarea programului
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Ore de Funcționare
        </Typography>

        {/* Afișare mesaje de eroare/succes */}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        {/* Formular pentru setarea programului */}
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Selector pentru ora de început */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Ora de început"
                type="time"
                value={hours.start_time}
                onChange={(e) => setHours({ ...hours, start_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
                inputProps={{ step: 300 }} // Permite intervale de 5 minute
              />
            </Grid>
            {/* Selector pentru ora de sfârșit */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Ora de sfârșit"
                type="time"
                value={hours.end_time}
                onChange={(e) => setHours({ ...hours, end_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
                inputProps={{ step: 300 }}
              />
            </Grid>
            {/* Selector pentru interval */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Interval (minute)"
                type="number"
                value={hours.interval}
                onChange={(e) => setHours({ ...hours, interval: e.target.value })}
                InputLabelProps={{ shrink: true }}
                inputProps={{ min: 15, max: 120 }} // Limitează intervalul între 15 și 120 minute
              />
            </Grid>
          </Grid>

          {/* Buton de salvare */}
          <Button
            type="submit"
            variant="contained"
            startIcon={<Save />}
            sx={{ mt: 3 }}
          >
            Salvează
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default BusinessHours; 