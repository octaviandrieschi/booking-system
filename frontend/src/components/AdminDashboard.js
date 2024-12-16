// Componenta pentru panoul de administrare
// Permite administratorilor să gestioneze serviciile disponibile în sistem

import React, { useState, useEffect } from "react";
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Alert,
  Box,
  CircularProgress,
  Tooltip,
  Grid,
  MenuItem,
} from "@mui/material";

import {
  Edit as EditIcon,
  Close as CloseIcon,
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";

function AdminDashboard() {
  const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:5000";
  
  // State-uri pentru gestionarea datelor și stării componentei
  const [services, setServices] = useState([]); // Lista serviciilor
  const [loading, setLoading] = useState(true); // Indicator pentru încărcare
  const [error, setError] = useState(""); // Mesaje de eroare
  const [success, setSuccess] = useState(""); // Mesaje de succes
  const [dialogOpen, setDialogOpen] = useState(false); // Control dialog adăugare/editare
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false); // Control dialog ștergere
  const [serviceToDelete, setServiceToDelete] = useState(null); // Serviciul selectat pentru ștergere
  const [editMode, setEditMode] = useState(false); // Mod editare vs. adăugare
  const [selectedService, setSelectedService] = useState(null); // Serviciul selectat pentru editare
  
  // State pentru formularul de serviciu
  const [formData, setFormData] = useState({
    category_id: '',
    name: "",
    description: "",
    price: "",
    start_time: "09:00",
    end_time: "17:00",
    interval: "30",
  });

  // Add state for categories
  const [categories, setCategories] = useState([]);

  // Resetează formularul la valorile inițiale
  const resetForm = () => {
    setFormData({
      category_id: "",
      name: "",
      description: "",
      price: "",
      start_time: "09:00",
      end_time: "17:00",
      interval: "30",
    });
    setEditMode(false);
    setSelectedService(null);
  };

  // Gestionează începerea editării unui serviciu
  const handleEdit = (service) => {
    setSelectedService(service);
    setFormData({
      category_id: service.category_id.toString(),
      name: service.name,
      description: service.description,
      price: service.price,
      start_time: service.start_time,
      end_time: service.end_time,
      interval: service.interval,
    });
    setEditMode(true);
    setDialogOpen(true);
  };

  // Gestionează trimiterea formularului (adăugare sau editare)
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Clear previous messages
    setError("");
    setSuccess("");

    try {
      // Convert form data to proper types
      const serviceData = {
        category_id: parseInt(formData.category_id),
        name: formData.name.trim(),
        description: formData.description.trim(),
        price: parseFloat(formData.price),
        start_time: formData.start_time,
        end_time: formData.end_time,
        interval: parseInt(formData.interval)
      };

      const response = await fetch(editMode ? `${apiUrl}/api/services/${selectedService.id}` : `${apiUrl}/api/services`, {
        method: editMode ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(serviceData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Eroare la salvarea serviciului");
      }

      setSuccess(editMode ? "Serviciu actualizat cu succes!" : "Serviciu adăugat cu succes!");
      setDialogOpen(false);
      resetForm();
      fetchData();
    } catch (error) {
      console.error("Eroare la trimiterea serviciului:", error);
      console.log("Date formular la momentul erorii:", formData);
      setError(error.message || "Eroare la salvarea serviciului");
    }
  };

  // Gestionează click-ul pe butonul de ștergere
  const handleDeleteClick = (service) => {
    setServiceToDelete(service);
    setDeleteDialogOpen(true);
  };

  // Gestionează confirmarea ștergerii
  const handleDeleteConfirm = async () => {
    // Clear previous messages
    setError("");
    setSuccess("");

    try {
      const response = await fetch(
        `${apiUrl}/api/services/${serviceToDelete.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Nu s-a putut șterge serviciul");
      }

      setSuccess("Serviciu șters cu succes!");
      fetchData();
    } catch (error) {
      setError(error.message);
    } finally {
      setDeleteDialogOpen(false);
      setServiceToDelete(null);
    }
  };

  // Preia lista de servicii de la server
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(""); // Clear any previous errors

      // Fetch both services and categories
      const [servicesResponse, categoriesResponse] = await Promise.all([
        fetch(`${apiUrl}/api/services`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
        fetch(`${apiUrl}/api/categories`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
      ]);

      if (!servicesResponse.ok || !categoriesResponse.ok) {
        throw new Error("Nu s-au putut prelua datele");
      }

      const [servicesData, categoriesData] = await Promise.all([
        servicesResponse.json(),
        categoriesResponse.json(),
      ]);

      if (Array.isArray(servicesData)) {
        setServices(servicesData);
      }
      if (Array.isArray(categoriesData)) {
        setCategories(categoriesData);
      }
    } catch (error) {
      console.error("Eroare la preluarea datelor:", error);
      setError("Nu s-au putut încărca datele");
    } finally {
      setLoading(false);
    }
  };

  // Încarcă serviciile la montarea componentei
  useEffect(() => {
    fetchData();
  }, []);

  // Add useEffect to clear messages after timeout
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError("");
        setSuccess("");
      }, 3000); // Messages will disappear after 3 seconds

      return () => clearTimeout(timer);
    }
  }, [error, success]);

  // Randarea interfeței de administrare
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={3}
        >
          <Typography variant="h4">Administrare Servicii</Typography>
          <Tooltip title="Adaugă Serviciu">
            <IconButton
              color="primary"
              onClick={() => {
                resetForm();
                setDialogOpen(true);
              }}
            >
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            onClose={() => setError("")}  // Allow manual close
          >
            {error}
          </Alert>
        )}

        {success && (
          <Alert 
            severity="success" 
            sx={{ mb: 2 }}
            onClose={() => setSuccess("")}  // Allow manual close
          >
            {success}
          </Alert>
        )}

        {services.length === 0 ? (
          <Box textAlign="center" py={3}>
            <Typography color="textSecondary">
              Nu există servicii înregistrate
            </Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Categorie</TableCell>
                  <TableCell>Nume</TableCell>
                  <TableCell>Descriere</TableCell>
                  <TableCell>Preț (RON)</TableCell>
                  <TableCell>Program</TableCell>
                  <TableCell align="right">Acțiuni</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {services.map((service) => (
                  <TableRow key={service.id}>
                    <TableCell>{service.category_name}</TableCell>
                    <TableCell>{service.name}</TableCell>
                    <TableCell>{service.description}</TableCell>
                    <TableCell>{service.price}</TableCell>
                    <TableCell>
                      {service.start_time} - {service.end_time}
                      <br />
                      <Typography variant="caption" color="textSecondary">
                        Interval: {service.interval} min
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Editează">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleEdit(service)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Șterge">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteClick(service)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
          <DialogTitle>
            {editMode ? "Editează Serviciu" : "Adaugă Serviciu Nou"}
          </DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <TextField
                fullWidth
                select
                label="Categorie"
                name="category_id"
                value={formData.category_id}
                onChange={(e) => {
                  setFormData({ ...formData, category_id: e.target.value });
                }}
                margin="normal"
                required
                error={!formData.category_id}
                helperText={!formData.category_id ? "Categoria este obligatorie" : ""}
              >
                <MenuItem value="" disabled>
                  Selectează categoria
                </MenuItem>
                {categories.map((category) => (
                  <MenuItem 
                    key={category.id} 
                    value={category.id.toString()}
                  >
                    {category.name}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                fullWidth
                label="Nume"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Descriere"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                margin="normal"
                multiline
                rows={3}
              />
              <TextField
                fullWidth
                label="Preț (RON)"
                value={formData.price}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === "" || (parseFloat(value) >= 0 && /^\d*\.?\d{0,2}$/.test(value))) {
                    setFormData({ ...formData, price: value });
                  }
                }}
                margin="normal"
                required
                type="number"
                inputProps={{ min: "0", step: "0.01" }}
                error={formData.price !== "" && (isNaN(parseFloat(formData.price)) || parseFloat(formData.price) <= 0)}
                helperText={formData.price !== "" && (isNaN(parseFloat(formData.price)) || parseFloat(formData.price) <= 0) 
                  ? "Prețul trebuie să fie un număr pozitiv" 
                  : ""}
              />

              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
                Program de Lucru
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Ora început"
                    type="time"
                    value={formData.start_time}
                    onChange={(e) =>
                      setFormData({ ...formData, start_time: e.target.value })
                    }
                    InputLabelProps={{ shrink: true }}
                    inputProps={{
                      step: 300,
                      hourCycle: "h23",
                    }}
                    sx={{
                      "& input": {
                        "&::-webkit-calendar-picker-indicator": {
                          filter: "invert(0.5)",
                        },
                        "&::-webkit-datetime-edit": {
                          hourCycle: "h23",
                        },
                      },
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Ora sfârșit"
                    type="time"
                    value={formData.end_time}
                    onChange={(e) =>
                      setFormData({ ...formData, end_time: e.target.value })
                    }
                    InputLabelProps={{ shrink: true }}
                    inputProps={{
                      step: 300,
                      hourCycle: "h23",
                    }}
                    sx={{
                      "& input": {
                        "&::-webkit-calendar-picker-indicator": {
                          filter: "invert(0.5)",
                        },
                        "&::-webkit-datetime-edit": {
                          hourCycle: "h23",
                        },
                      },
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Interval (minute)"
                    value={formData.interval}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "" || (parseInt(value) >= 15 && /^\d+$/.test(value))) {
                        setFormData({ ...formData, interval: value });
                      }
                    }}
                    margin="normal"
                    required
                    type="number"
                    inputProps={{ min: "15", step: "15" }}
                    error={formData.interval !== "" && (isNaN(parseInt(formData.interval)) || parseInt(formData.interval) < 15)}
                    helperText={formData.interval !== "" && (isNaN(parseInt(formData.interval)) || parseInt(formData.interval) < 15)
                      ? "Intervalul trebuie să fie de cel puțin 15 minute"
                      : ""}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>Anulează</Button>
              <Button type="submit" variant="contained">
                {editMode ? "Salvează" : "Adaugă"}
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        <Dialog
          open={deleteDialogOpen}
          onClose={() => setDeleteDialogOpen(false)}
        >
          <DialogTitle>Confirmare ștergere</DialogTitle>
          <DialogContent>
            <Typography>
              Sigur doriți să ștergei serviciul "{serviceToDelete?.name}"?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => setDeleteDialogOpen(false)}
              startIcon={<CloseIcon />}
            >
              Anulează
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              color="error"
              variant="contained"
              startIcon={<DeleteIcon />}
            >
              Șterge
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Container>
  );
}

export default AdminDashboard;
