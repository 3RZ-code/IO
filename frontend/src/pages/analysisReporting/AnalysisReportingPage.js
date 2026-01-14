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
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import AssessmentIcon from "@mui/icons-material/Assessment";
import AddIcon from "@mui/icons-material/Add";
import RefreshIcon from "@mui/icons-material/Refresh";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import api from "../../api/axios";
import analysisReportingApi from "../../api/analysisReporting/analysisReportingApi";
import GenerateReportDialog from "../../components/analysisReporting/GenerateReportDialog";
import CompareReportsDialog from "../../components/analysisReporting/CompareReportsDialog";
import ReportCard from "../../components/analysisReporting/ReportCard";

function AnalysisReportingPage() {
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [error, setError] = useState(null);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [compareDialogOpen, setCompareDialogOpen] = useState(false);
  const [selectedReportForCompare, setSelectedReportForCompare] =
    useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

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
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analysisReportingApi.getAllReports();
      setReports(data);
    } catch (err) {
      console.error("Error loading reports:", err);
      setError("Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const handleReportGenerated = (report) => {
    setSnackbar({
      open: true,
      message: "Report generated successfully!",
      severity: "success",
    });
    loadReports();
  };

  const handleViewReport = (report) => {
    navigate(`/analysis-reporting/report/${report.report_id}`);
  };

  const handleDeleteReport = async (reportId) => {
    if (!window.confirm("Are you sure you want to delete this report?")) {
      return;
    }

    try {
      await analysisReportingApi.deleteReport(reportId);
      setSnackbar({
        open: true,
        message: "Report deleted successfully",
        severity: "success",
      });
      loadReports();
    } catch (err) {
      console.error("Error deleting report:", err);
      setSnackbar({
        open: true,
        message: "Failed to delete report",
        severity: "error",
      });
    }
  };

  const handleExportReport = async (reportId, format) => {
    try {
      if (format === "pdf") {
        await analysisReportingApi.exportReportPDF(reportId);
        setSnackbar({
          open: true,
          message: "PDF exported successfully",
          severity: "success",
        });
      } else if (format === "json") {
        const data = await analysisReportingApi.exportReport(reportId);
        analysisReportingApi.downloadJSON(data, `report_${reportId}.json`);
        setSnackbar({
          open: true,
          message: "JSON exported successfully",
          severity: "success",
        });
      }
    } catch (err) {
      console.error("Error exporting report:", err);
      setSnackbar({
        open: true,
        message: `Failed to export ${format.toUpperCase()}`,
        severity: "error",
      });
    }
  };

  const handleCompareReport = (report) => {
    setSelectedReportForCompare(report);
    setCompareDialogOpen(true);
  };

  const handleComparisonCreated = (comparison) => {
    setSnackbar({
      open: true,
      message: "Comparison created successfully!",
      severity: "success",
    });
    // Navigate to comparison view if needed
    // navigate(`/analysis-reporting/comparison/${comparison.report_compare_id}`);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box
      className="AnalysisReportingPage"
      sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
    >
      <AppBar position="static">
        <Toolbar>
          <IconButton
            color="inherit"
            onClick={() => navigate("/")}
            sx={{ mr: 2 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Analysis & Reporting
          </Typography>
          {isAdmin && (
            <IconButton
              color="inherit"
              onClick={() => navigate("/admin")}
              sx={{ mr: 1 }}
            >
              <AdminPanelSettingsIcon />
            </IconButton>
          )}
          <IconButton
            color="inherit"
            onClick={() => navigate("/profile")}
            sx={{ mr: 2 }}
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
          <AssessmentIcon sx={{ fontSize: 80, color: "#fff", mb: 2 }} />
          <Typography variant="h3" component="h1" gutterBottom>
            Analysis & Reporting
          </Typography>
          <Typography variant="h6" color="inherit" paragraph>
            Generate comprehensive reports, analyze trends, detect anomalies,
            and compare data across different time periods.
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<AddIcon />}
            onClick={() => setGenerateDialogOpen(true)}
            sx={{
              mt: 2,
              bgcolor: "white",
              color: "primary.main",
              "&:hover": { bgcolor: "grey.100" },
            }}
          >
            Generate New Report
          </Button>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 3, flexGrow: 1 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h5">Your Reports</Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadReports}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {!loading && !error && reports.length === 0 && (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <AssessmentIcon sx={{ fontSize: 80, color: "grey.400", mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No reports yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Generate your first report to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setGenerateDialogOpen(true)}
            >
              Generate Report
            </Button>
          </Box>
        )}

        {!loading && !error && reports.length > 0 && (
          <Grid container spacing={3}>
            {reports.map((report) => (
              <Grid item xs={12} md={6} lg={4} key={report.report_id}>
                <ReportCard
                  report={report}
                  onView={handleViewReport}
                  onDelete={handleDeleteReport}
                  onExport={handleExportReport}
                  onCompare={handleCompareReport}
                />
              </Grid>
            ))}
          </Grid>
        )}
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

      {/* Dialogs */}
      <GenerateReportDialog
        open={generateDialogOpen}
        onClose={() => setGenerateDialogOpen(false)}
        onReportGenerated={handleReportGenerated}
      />

      <CompareReportsDialog
        open={compareDialogOpen}
        onClose={() => setCompareDialogOpen(false)}
        reports={reports}
        selectedReport={selectedReportForCompare}
        onComparisonCreated={handleComparisonCreated}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default AnalysisReportingPage;
