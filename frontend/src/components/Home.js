import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Alert
} from "@mui/material";
import { CalendarMonth } from "@mui/icons-material";

function Home() {
  // State-uri pentru gestionarea datelor și UI
  const [services, setServices] = useState([]); // Lista serviciilor disponibile
  const [loading, setLoading] = useState(true); // Indicator pentru încărcare
  const [error, setError] = useState(null); // Mesaje de eroare
  const navigate = useNavigate();

  // Efect pentru încărcarea serviciilor la montarea componentei
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        const response = await fetch(`${apiUrl}/api/services`);

        if (!response.ok) {
          throw new Error('Nu s-au putut încărca serviciile');
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

  // Afișează indicator de încărcare
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  // Randarea interfeței principale
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Secțiunea de bun venit */}
      <Box textAlign="center" mb={6}>
        <Typography variant="h3" component="h1" gutterBottom>
          Sistem de Programări Online
        </Typography>
        <Typography variant="h5" color="textSecondary" paragraph>
          Rezervați simplu și rapid serviciile dorite
        </Typography>
        <Button
          variant="contained"
          size="large"
          startIcon={<CalendarMonth />}
          onClick={() => navigate('/book')}
          sx={{ mt: 2 }}
        >
          Programează-te Acum
        </Button>
      </Box>

      {/* Afișare erori */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {/* Grid cu servicii disponibile */}
      <Grid container spacing={4}>
        {services.map((service) => (
          <Grid item key={service.id} xs={12} sm={6} md={4}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {service.name}
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {service.description}
                </Typography>
                <Typography variant="h6" color="primary">
                  {service.price} RON
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  color="primary"
                  onClick={() => navigate('/book', { state: { selectedServiceId: service.id } })}
                >
                  Programează
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default Home;
