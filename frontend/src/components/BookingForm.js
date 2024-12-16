// Componenta pentru formularul de programare
// Permite utilizatorilor să aleagă un serviciu și să facă o programare

import React, { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Container,
  Paper,
  Box,
  Typography,
  TextField,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
} from "@mui/material";
import { CalendarMonth } from "@mui/icons-material";

function BookingForm() {
  // State-uri pentru gestionarea datelor formularului
  const location = useLocation();
  // Get the selected service ID from navigation state
  const preselectedServiceId = location.state?.selectedServiceId;
  
  const [services, setServices] = useState([]); // Lista serviciilor disponibile
  const [selectedService, setSelectedService] = useState(preselectedServiceId || "");
  const [selectedDate, setSelectedDate] = useState(""); // Data selectată
  const [selectedTime, setSelectedTime] = useState(""); // Ora selectată
  const [availableTimes, setAvailableTimes] = useState([]); // Orele disponibile pentru data selectată
  const [loading, setLoading] = useState(true); // Indicator pentru încărcare
  const [error, setError] = useState(null); // Mesaje de eroare
  const navigate = useNavigate();

  // Funcție pentru preluarea intervalelor disponibile de la server
  const fetchAvailableSlots = useCallback(async (date) => {
    if (!selectedService || !date) return;

    try {
      const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:5000";
      const response = await fetch(
        `${apiUrl}/api/appointments/available-slots?date=${date}&service_id=${selectedService}`
      );

      if (!response.ok) {
        throw new Error("Nu s-au putut încărca intervalele disponibile");
      }

      const data = await response.json();
      setAvailableTimes(data.slots);
    } catch (err) {
      setError(err.message);
    }
  }, [selectedService]);

  // Efect pentru încărcarea inițială a serviciilor
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:5000";
        const response = await fetch(`${apiUrl}/api/services`);

        if (!response.ok) {
          throw new Error("Nu s-au putut încărca serviciile");
        }

        const data = await response.json();
        setServices(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  // Efect pentru actualizarea intervalelor disponibile când se schimbă data sau serviciul
  useEffect(() => {
    if (selectedDate) {
      fetchAvailableSlots(selectedDate);
    }
  }, [selectedDate, selectedService, fetchAvailableSlots]);

  // Gestionează trimiterea formularului
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedService || !selectedDate || !selectedTime) {
      setError("Vă rugăm să completați toate câmpurile");
      return;
    }

    try {
      const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:5000";
      const response = await fetch(`${apiUrl}/api/appointments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          service_id: selectedService,
          date_time: `${selectedDate}T${selectedTime}:00`,
        }),
      });

      if (!response.ok) {
        throw new Error("Nu s-a putut crea programarea");
      }

      const data = await response.json();
      navigate(`/receipt/${data.appointment_id}`);
    } catch (err) {
      setError(err.message);
    }
  };

  // Afișează indicator de încărcare
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  // Randarea formularului
  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box display="flex" flexDirection="column" alignItems="center" mb={4}>
            <CalendarMonth sx={{ fontSize: 40, color: "primary.main", mb: 2 }} />
            <Typography component="h1" variant="h5">
              Rezervare Serviciu
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            {/* Selector serviciu */}
            <TextField
              select
              fullWidth
              label="Serviciu"
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              sx={{ mb: 3 }}
            >
              {services.map((service) => (
                <MenuItem key={service.id} value={service.id}>
                  {service.name} - {service.price} RON
                </MenuItem>
              ))}
            </TextField>

            {/* Show date selector only when service is selected */}
            {selectedService && (
              <TextField
                fullWidth
                label="Data"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                sx={{ mb: 3 }}
                InputLabelProps={{ shrink: true }}
                inputProps={{
                  min: new Date().toISOString().split("T")[0],
                }}
              />
            )}

            {/* Selector oră */}
            {selectedDate && selectedService && (
              <>
                {availableTimes.length > 0 ? (
                  <TextField
                    select
                    fullWidth
                    label="Ora"
                    value={selectedTime}
                    onChange={(e) => setSelectedTime(e.target.value)}
                    sx={{ mb: 3 }}
                  >
                    {availableTimes.map((time) => (
                      <MenuItem key={time} value={time}>
                        {time}
                      </MenuItem>
                    ))}
                  </TextField>
                ) : (
                  <Alert severity="info" sx={{ mb: 3 }}>
                    Nu există intervale disponibile pentru data selectată
                  </Alert>
                )}
              </>
            )}

            {/* Buton de confirmare */}
            <Button 
              type="submit" 
              fullWidth 
              variant="contained" 
              sx={{ mt: 3 }}
              disabled={!selectedService || !selectedDate || !selectedTime}
            >
              Confirmă Programarea
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default BookingForm;
