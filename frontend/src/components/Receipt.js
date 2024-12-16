// Componenta pentru afișarea chitanței
// Permite vizualizarea detaliilor unei chitanțe pentru o programare

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Divider,
  CircularProgress,
  Alert,
  Button
} from "@mui/material";
import { Print, Receipt as ReceiptIcon, Download, ArrowBack } from "@mui/icons-material";

function Receipt() {
  // State-uri pentru gestionarea datelor și UI
  const [receipt, setReceipt] = useState(null);     // Datele chitanței
  const [loading, setLoading] = useState(true);     // Indicator pentru încărcare
  const [error, setError] = useState(null);         // Mesaje de eroare
  const { id } = useParams();                       // ID-ul programării din URL
  const navigate = useNavigate();

  // Efect pentru încărcarea datelor chitanței
  useEffect(() => {
    const fetchReceipt = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        const response = await fetch(`${apiUrl}/api/receipts/${id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Nu s-a putut încărca chitanța');
        }

        const data = await response.json();
        setReceipt(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReceipt();
  }, [id]);

  // Funcție pentru formatarea datei
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ro-RO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Funcție pentru printarea chitanței
  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/receipts/${id}/pdf`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Nu s-a putut descărca PDF-ul');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `receipt_${receipt.receipt_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
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

  // Randarea chitanței
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={() => navigate('/appointments')}
        >
          Înapoi la programări
        </Button>
      </Box>

      <Paper elevation={3} sx={{ p: 4 }} className="print-content">
        <Box display="flex" flexDirection="column" alignItems="center" mb={4}>
          <ReceiptIcon sx={{ fontSize: 40, color: "primary.main", mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Confirmare Rezervare
          </Typography>
        </Box>

        {/* Afișare erori */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        {receipt && (
          <>
            {/* Detalii chitanță */}
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle1">
                  Număr chitanță: {receipt.receipt_number}
                </Typography>
                <Typography variant="subtitle1">
                  Data emiterii: {formatDate(receipt.date_issued)}
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <Divider />
              </Grid>

              {/* Detalii client */}
              <Grid item xs={12} sm={6}>
                <Typography variant="h6" gutterBottom>
                  Client
                </Typography>
                <Typography>{receipt.client_name}</Typography>
                <Typography>{receipt.client_email}</Typography>
              </Grid>

              {/* Detalii serviciu */}
              <Grid item xs={12} sm={6}>
                <Typography variant="h6" gutterBottom>
                  Serviciu
                </Typography>
                <Typography>{receipt.service_name}</Typography>
                <Typography>
                  Data programării: {formatDate(receipt.date_time)}
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <Divider />
              </Grid>

              {/* Total de plată */}
              <Grid item xs={12}>
                <Typography variant="h6" align="right">
                  Total: {receipt.total} RON
                </Typography>
              </Grid>
            </Grid>

            {/* Buton printare */}
            <Box display="flex" justifyContent="center" gap={2} mt={4} className="no-print">
              <Button
                variant="contained"
                startIcon={<Print />}
                onClick={handlePrint}
              >
                Printează Chitanța
              </Button>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={handleDownloadPDF}
              >
                Descarcă PDF
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Container>
  );
}

export default Receipt;
