import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import SettingsIcon from "@mui/icons-material/Settings";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import AlarmIcon from "@mui/icons-material/Alarm";
import AssessmentIcon from "@mui/icons-material/Assessment";
import ForumIcon from "@mui/icons-material/Forum";
import StorageIcon from "@mui/icons-material/Storage";
import TimelineIcon from "@mui/icons-material/Timeline";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import SecurityIcon from "@mui/icons-material/Security";
import ScienceIcon from "@mui/icons-material/Science";
import NotificationBell from "../components/NotificationBell";
import api from "../api/axios";

const modules = [
  {
    name: "Alarm & Alert",
    icon: <AlarmIcon fontSize="large" color="primary" />,
    desc: "Real-time alarm notifications and alert handling.",
    path: "/alerts",
  },
  {
    name: "Analysis & Reporting",
    icon: <AssessmentIcon fontSize="large" color="primary" />,
    desc: "In-depth data analysis and reporting tools.",
    path: "/analysis-reporting",
  },
  {
    name: "Communication",
    icon: <ForumIcon fontSize="large" color="primary" />,
    desc: "Reliable communication between system modules.",
    path: "/communication",
  },
  {
    name: "Data Acquisition",
    icon: <StorageIcon fontSize="large" color="primary" />,
    desc: "Efficient data collection from multiple sources.",
    path: null,
  },
  {
    name: "Forecasting",
    icon: <TimelineIcon fontSize="large" color="primary" />,
    desc: "Predictive analytics and trend forecasting.",
    path: null,
  },
  {
    name: "Optimization & Control",
    icon: <SettingsSuggestIcon fontSize="large" color="primary" />,
    desc: "Smart optimization and advanced control systems.",
    path: "/optimization",
  },
  {
    name: "Security",
    icon: <SecurityIcon fontSize="large" color="primary" />,
    desc: "Comprehensive security and access management.",
    path: null,
  },
  {
    name: "Simulation",
    icon: <ScienceIcon fontSize="large" color="primary" />,
    desc: "Modeling and simulation of system scenarios.",
    path: null,
  },
];

function MainPage() {
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const response = await api.get("/security/users/me/");
        setIsAdmin(response.data.role === "admin");
      } catch (err) {
        console.error(err);
      }
    };
    checkAdmin();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <Box
      className="MainPage"
      sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
    >
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Smart System Platform
          </Typography>
          <IconButton
            color="inherit"
            onClick={() => navigate("/alerts")}
            sx={{ mr: 1 }}
            title="Alerty"
          >
            <AlarmIcon />
          </IconButton>
          <NotificationBell />
          <IconButton
            color="inherit"
            onClick={() => navigate("/notification-preferences")}
            sx={{ mr: 1 }}
            title="Ustawienia powiadomień"
          >
            <SettingsIcon />
          </IconButton>
          {isAdmin && (
            <IconButton
              color="inherit"
              onClick={() => navigate("/admin")}
              sx={{ mr: 1 }}
              title="Panel administratora"
            >
              <AdminPanelSettingsIcon />
            </IconButton>
          )}
          <IconButton
            color="inherit"
            onClick={() => navigate("/profile")}
            sx={{ mr: 2 }}
            title="Profil"
          >
            <AccountCircleIcon />
          </IconButton>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Box className="hero-section" sx={{ py: 8 }}>
        <Container maxWidth="md" sx={{ textAlign: "center" }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Welcome to Smart System Platform
          </Typography>
          <Typography variant="h6" color="text.secondary" paragraph>
            Integrate, analyze, and optimize your operations with advanced
            modules for data acquisition, forecasting, simulation, and more.
          </Typography>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Grid
          className="grid-modules"
          container
          spacing={3}
          sx={{ justifyContent: "center", display: "flex" }}
        >
          {modules.map((mod) => (
            <Grid item xs={12} sm={6} md={3} key={mod.name} display="flex">
              <Paper
                elevation={4}
                className="module-square"
                onClick={() => {
                  if (mod.name === "Analysis & Reporting") {
                    navigate("/analysis-reporting");
                  }
                }}
                sx={{
                  aspectRatio: "1/1",
                  width: "300px",
                  justifyContent: "center",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  p: 3,
                  minWidth: 0,
                  minHeight: 0,
                  textAlign: "center",
                  cursor:
                    mod.name === "Analysis & Reporting" ? "pointer" : "default",
                  transition: "transform 0.2s, box-shadow 0.2s",
                  cursor: mod.path ? "pointer" : "default",
                  "&:hover": {
                    transform: mod.path ? "translateY(-5px) scale(1.03)" : "none",
                    boxShadow: mod.path
                      ? "0 8px 24px rgba(33, 150, 243, 0.18)"
                      : "0 4px 6px rgba(0, 0, 0, 0.1)",
                  },
                }}
                onClick={() => mod.path && navigate(mod.path)}
              >
                {mod.icon}
                <Typography variant="h6" sx={{ mt: 2 }}>
                  {mod.name}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 1 }}
                >
                  {mod.desc}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box
        component="footer"
        sx={{ py: 3, background: "#1976d2", color: "#fff", mt: "auto" }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" align="center">
            &copy; {new Date().getFullYear()} Smart System Platform. All rights
            reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

export default MainPage;
