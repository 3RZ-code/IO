import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Card,
  CardContent,
  IconButton,
} from "@mui/material";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import DownloadIcon from "@mui/icons-material/Download";
import ScienceIcon from "@mui/icons-material/Science";
import analysisReportingApi from "../../api/analysisReporting/analysisReportingApi";
import api from "../../api/axios";

function ReportDetailsPage() {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [generatingAnomaly, setGeneratingAnomaly] = useState(false);

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

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reportId]);

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analysisReportingApi.getReportById(reportId);
      setReport(data);
    } catch (err) {
      console.error("Error loading report:", err);
      setError("Failed to load report details");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const handleExportPDF = async () => {
    try {
      await analysisReportingApi.exportReportPDF(reportId);
    } catch (err) {
      console.error("Error exporting PDF:", err);
      alert("Failed to export PDF");
    }
  };

  const handleExportJSON = async () => {
    try {
      const data = await analysisReportingApi.exportReport(reportId);
      analysisReportingApi.downloadJSON(data, `report_${reportId}.json`);
    } catch (err) {
      console.error("Error exporting JSON:", err);
      alert("Failed to export JSON");
    }
  };

  const handleGenerateAnomaly = async () => {
    setGeneratingAnomaly(true);
    try {
      await analysisReportingApi.generateAnomalyAnalysis(reportId, {
        generate_chart: true,
        use_ai: false,
      });
      // Reload report to show new analysis
      await loadReport();
      alert("Anomaly analysis generated successfully!");
    } catch (err) {
      console.error("Error generating anomaly:", err);
      alert("Failed to generate anomaly analysis");
    } finally {
      setGeneratingAnomaly(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("pl-PL", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatAnalysisSummary = (analysis) => {
    if (!analysis.analysis_summary) return "Brak podsumowania";

    try {
      // Parsuj JSON z analysis_summary
      const summaryData =
        typeof analysis.analysis_summary === "string"
          ? JSON.parse(analysis.analysis_summary)
          : analysis.analysis_summary;

      // Jeśli jest pole 'summary', użyj go
      if (summaryData.summary) {
        return summaryData.summary;
      }

      // W przeciwnym razie wygeneruj czytelny opis z danych
      if (analysis.analysis_type === "TRENDS") {
        const trend = summaryData.trend || "nieznany";
        const direction = summaryData.trend_direction || "N/A";
        const changePercent = summaryData.change_percentage || 0;
        const firstAvg = summaryData.first_period_avg || 0;
        const secondAvg = summaryData.second_period_avg || 0;

        return `Analiza trendu wykazała ${
          trend === "stable"
            ? "stabilny poziom"
            : trend === "increasing"
            ? "wzrost"
            : "spadek"
        } wartości. Kierunek: ${direction}, zmiana: ${changePercent.toFixed(
          2
        )}%. Średnia w pierwszym okresie: ${firstAvg.toFixed(
          2
        )}, w drugim: ${secondAvg.toFixed(2)}.`;
      }

      if (analysis.analysis_type === "PEAK") {
        const peakValue = summaryData.peak_value || 0;
        const avgValue = summaryData.average_value || 0;
        const peakTime = summaryData.peak_timestamp || "N/A";

        return `Analiza szczytów obciążenia. Maksymalna wartość: ${peakValue.toFixed(
          2
        )} (czas: ${peakTime}). Średnia wartość: ${avgValue.toFixed(
          2
        )}. Szczyt stanowi ${((peakValue / avgValue - 1) * 100).toFixed(
          2
        )}% powyżej średniej.`;
      }

      if (analysis.analysis_type === "ANOMALY") {
        const anomalyCount = summaryData.anomalies?.length || 0;
        const threshold = summaryData.threshold || "N/A";

        return `Wykryto ${anomalyCount} anomalii w danych. Próg detekcji: ${threshold}. ${
          anomalyCount > 0
            ? "Anomalie mogą wskazywać na nietypowe warunki operacyjne lub problemy z urządzeniami."
            : "Wszystkie odczyty mieszczą się w normalnym zakresie."
        }`;
      }

      // Fallback - pokaż jako JSON
      return JSON.stringify(summaryData, null, 2);
    } catch (error) {
      console.error("Error parsing analysis summary:", error);
      return analysis.analysis_summary;
    }
  };

  const hasAnomalyAnalysis = report?.analyses?.some(
    (a) => a.analysis_type === "ANOMALY"
  );

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error || !report) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error || "Report not found"}</Alert>
        <Button onClick={() => navigate("/analysis-reporting")} sx={{ mt: 2 }}>
          Back to Reports
        </Button>
      </Box>
    );
  }

  const criteria = report.report_criteria || {};

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            color="inherit"
            onClick={() => navigate("/analysis-reporting")}
            sx={{ mr: 2 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Report Details
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

      <Container maxWidth="lg" sx={{ py: 4, flexGrow: 1 }}>
        {/* Header Actions */}
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
          <Typography variant="h4">Report Details</Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<PictureAsPdfIcon />}
              onClick={handleExportPDF}
            >
              Export PDF
            </Button>
            <Button
              variant="outlined"
              color="success"
              startIcon={<DownloadIcon />}
              onClick={handleExportJSON}
            >
              Export JSON
            </Button>
          </Box>
        </Box>

        {/* Report Info */}
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Report Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Report ID:
              </Typography>
              <Typography variant="body1" sx={{ fontFamily: "monospace" }}>
                {report.report_id}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Created:
              </Typography>
              <Typography variant="body1">
                {formatDate(report.created_timestamp)}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Description:
              </Typography>
              <Typography variant="body1">
                {report.report_description || "No description"}
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Criteria */}
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Report Criteria
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Location:
              </Typography>
              <Typography variant="body1">
                {criteria.location || "All locations"}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Device Type:
              </Typography>
              <Typography variant="body1">
                {criteria.device_type || "All types"}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Date From:
              </Typography>
              <Typography variant="body1">
                {criteria.date_created_from}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Date To:
              </Typography>
              <Typography variant="body1">
                {criteria.date_created_to}
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Analyses */}
        <Box sx={{ mb: 3 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">Analyses</Typography>
            {!hasAnomalyAnalysis && (
              <Button
                variant="contained"
                color="error"
                startIcon={<ScienceIcon />}
                onClick={handleGenerateAnomaly}
                disabled={generatingAnomaly}
              >
                {generatingAnomaly
                  ? "Generating..."
                  : "Generate Anomaly Analysis"}
              </Button>
            )}
          </Box>

          <Grid container spacing={2}>
            {report.analyses?.map((analysis) => (
              <Grid item xs={12} key={analysis.analysis_id}>
                <Card elevation={2}>
                  <CardContent>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mb: 2,
                      }}
                    >
                      <Typography variant="h6">
                        {analysis.analysis_type} Analysis
                      </Typography>
                      <Chip
                        label={analysis.analysis_type}
                        color={
                          analysis.analysis_type === "TRENDS"
                            ? "primary"
                            : analysis.analysis_type === "PEAK"
                            ? "warning"
                            : "error"
                        }
                      />
                    </Box>

                    {analysis.analysis_summary && (
                      <Box sx={{ mb: 2 }}>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          Podsumowanie:
                        </Typography>
                        <Paper
                          elevation={0}
                          sx={{
                            p: 2,
                            bgcolor: "grey.100",
                            borderLeft: "4px solid",
                            borderColor:
                              analysis.analysis_type === "TRENDS"
                                ? "primary.main"
                                : analysis.analysis_type === "PEAK"
                                ? "warning.main"
                                : "error.main",
                          }}
                        >
                          <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
                            {formatAnalysisSummary(analysis)}
                          </Typography>
                        </Paper>
                      </Box>
                    )}

                    {analysis.visualizations &&
                      analysis.visualizations.length > 0 && (
                        <Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mb: 1 }}
                          >
                            Wizualizacje:
                          </Typography>
                          <Grid container spacing={2}>
                            {analysis.visualizations.map((viz) => (
                              <Grid
                                item
                                xs={12}
                                md={6}
                                key={viz.visualization_id}
                              >
                                <Paper elevation={1} sx={{ p: 1 }}>
                                  <img
                                    src={analysisReportingApi.getVisualizationUrl(
                                      viz.file_path
                                    )}
                                    alt={`${analysis.analysis_type} chart`}
                                    style={{
                                      width: "100%",
                                      height: "auto",
                                      display: "block",
                                    }}
                                    onError={(e) => {
                                      e.target.style.display = "none";
                                      e.target.nextSibling.style.display =
                                        "block";
                                    }}
                                  />
                                  <Typography
                                    variant="caption"
                                    color="error"
                                    sx={{
                                      display: "none",
                                      textAlign: "center",
                                    }}
                                  >
                                    Failed to load visualization
                                  </Typography>
                                </Paper>
                              </Grid>
                            ))}
                          </Grid>
                        </Box>
                      )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
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

export default ReportDetailsPage;
