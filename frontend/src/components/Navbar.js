import React from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  AccountCircle,
  CalendarMonth,
  Logout,
  AdminPanelSettings,
} from "@mui/icons-material";

function Navbar({ isLoggedIn, setIsLoggedIn }) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const navigate = useNavigate();
  const userRole = localStorage.getItem("userRole");

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userRole");
    setIsLoggedIn(false);
    navigate("/");
    handleClose();
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: "none",
            color: "inherit",
          }}
        >
          Booking System
        </Typography>

        {!isLoggedIn ? (
          <Box>
            <Button
              color="inherit"
              component={RouterLink}
              to="/login"
              startIcon={<AccountCircle />}
            >
              Autentificare
            </Button>
          </Box>
        ) : (
          <Box>
            <Button
              color="inherit"
              component={RouterLink}
              to={userRole === "admin" ? "/admin/bookings" : "/appointments"}
              startIcon={<CalendarMonth />}
            >
              {userRole === "admin" ? "Programări" : "Programările Mele"}
            </Button>

            <IconButton
              color="inherit"
              onClick={handleMenu}
              sx={{ ml: 1 }}
            >
              {userRole === "admin" ? <AdminPanelSettings /> : <AccountCircle />}
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              {userRole === "admin" && (
                <MenuItem
                  onClick={() => {
                    navigate("/admin");
                    handleClose();
                  }}
                >
                  Panou Admin
                </MenuItem>
              )}

              {userRole !== "admin" && (
                <MenuItem
                  onClick={() => {
                    navigate("/book");
                    handleClose();
                  }}
                >
                  Programare Nouă
                </MenuItem>
              )}

              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1 }} />
                Deconectare
              </MenuItem>
            </Menu>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
