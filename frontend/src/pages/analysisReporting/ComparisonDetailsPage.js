import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Divider,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingFlatIcon from "@mui/icons-material/TrendingFlat";
import analysisReportingApi from "../../api/analysisReporting/analysisReportingApi";
import api from "../../api/axios";

function ComparisonDetailsPage() {
  const { comparisonId } = useParams();
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comparison, setComparison] = useState(null);

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
    loadComparison();
  }, [comparisonId]);

  const loadComparison = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analysisReportingApi.getComparisonById(comparisonId);
      setComparison(data);
    } catch (err) {
      console.error("Error loading comparison:", err);
      setError("Failed to load comparison details");
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
      await analysisReportingApi.exportComparisonPDF(comparisonId);
    } catch (err) {
      console.error("Error exporting PDF:", err);
      alert("Failed to export PDF");
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

  const getTrendIcon = (trend) => {
    if (trend === "increasing" || trend === "up") {
      return <TrendingUpIcon color="error" />;
    } else if (trend === "decreasing" || trend === "down") {
      return <TrendingDownIcon color="success" />;
    }
    return <TrendingFlatIcon color="info" />;
  };

  const getTrendColor = (percentageChange) => {
    if (percentageChange > 10) return "error";
    if (percentageChange < -10) return "success";
    return "info";
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return "N/A";
    return Number(num).toFixed(2);
  };

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

  if (error || !comparison) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error || "Comparison not found"}</Alert>
        <Button onClick={() => navigate("/analysis-reporting")} sx={{ mt: 2 }}>
          Back to Reports
        </Button>
      </Box>
    );
  }

  const comparisonData =
    typeof comparison.comparison_description === "string"
      ? JSON.parse(comparison.comparison_description)
      : comparison.comparison_description;

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
            Report Comparison
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
          <Typography variant="h4">Report Comparison</Typography>
          <Button
            variant="outlined"
            color="error"
            startIcon={<PictureAsPdfIcon />}
            onClick={handleExportPDF}
          >
            Export PDF
          </Button>
        </Box>

        {/* Comparison Info - Hidden for now */}

        {/* Report Comparison */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: "100%" }}>
              <Typography variant="h6" gutterBottom color="primary">
                Raport Pierwszy
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  ID Raportu:
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ fontFamily: "monospace", wordBreak: "break-all" }}
                >
                  {comparison.report_one?.report_id}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Okres:
                </Typography>
                <Typography variant="body1">
                  {comparison.report_one?.report_criteria?.date_created_from} -{" "}
                  {comparison.report_one?.report_criteria?.date_created_to}
                </Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Lokalizacja:
                  </Typography>
                  <Chip
                    label={
                      comparison.report_one?.report_criteria?.location ||
                      "Wszystkie"
                    }
                    color="primary"
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Typ urządzenia:
                  </Typography>
                  <Chip
                    label={
                      comparison.report_one?.report_criteria?.device_type ||
                      "Wszystkie"
                    }
                    color="primary"
                    variant="outlined"
                    size="small"
                  />
                </Grid>
              </Grid>

              {comparisonData?.report_one && (
                <Box
                  sx={{
                    mt: 2,
                    p: 2,
                    bgcolor: "primary.light",
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2" color="white" fontWeight="bold">
                    Liczba pomiarów: {comparisonData.report_one.data_points}
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: "100%" }}>
              <Typography variant="h6" gutterBottom color="secondary">
                Raport Drugi
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  ID Raportu:
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ fontFamily: "monospace", wordBreak: "break-all" }}
                >
                  {comparison.report_two?.report_id}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Okres:
                </Typography>
                <Typography variant="body1">
                  {comparison.report_two?.report_criteria?.date_created_from} -{" "}
                  {comparison.report_two?.report_criteria?.date_created_to}
                </Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Lokalizacja:
                  </Typography>
                  <Chip
                    label={
                      comparison.report_two?.report_criteria?.location ||
                      "Wszystkie"
                    }
                    color="secondary"
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Typ urządzenia:
                  </Typography>
                  <Chip
                    label={
                      comparison.report_two?.report_criteria?.device_type ||
                      "Wszystkie"
                    }
                    color="secondary"
                    variant="outlined"
                    size="small"
                  />
                </Grid>
              </Grid>

              {comparisonData?.report_two && (
                <Box
                  sx={{
                    mt: 2,
                    p: 2,
                    bgcolor: "secondary.light",
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2" color="white" fontWeight="bold">
                    Liczba pomiarów: {comparisonData.report_two.data_points}
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Main Comparison Statistics */}
        {comparisonData?.comparison && (
          <>
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Główne Statystyki Porównawcze
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                {/* Percentage Change Card */}
                <Grid item xs={12} md={4}>
                  <Card
                    sx={{
                      height: "100%",
                      bgcolor:
                        getTrendColor(
                          comparisonData.comparison.percentage_change
                        ) === "error"
                          ? "error.light"
                          : getTrendColor(
                              comparisonData.comparison.percentage_change
                            ) === "success"
                          ? "success.light"
                          : "info.light",
                    }}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="h6" color="white">
                          Zmiana Procentowa
                        </Typography>
                        {getTrendIcon(comparisonData.comparison.trend)}
                      </Box>
                      <Typography variant="h3" color="white" fontWeight="bold">
                        {formatNumber(
                          comparisonData.comparison.percentage_change
                        )}
                        %
                      </Typography>
                      <Typography variant="body2" color="white" sx={{ mt: 1 }}>
                        Trend:{" "}
                        {comparisonData.comparison.trend === "increasing"
                          ? "Wzrostowy"
                          : comparisonData.comparison.trend === "decreasing"
                          ? "Spadkowy"
                          : "Stabilny"}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Absolute Difference Card */}
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: "100%", bgcolor: "grey.100" }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Różnica Bezwzględna
                      </Typography>
                      <Typography
                        variant="h3"
                        fontWeight="bold"
                        color="text.primary"
                      >
                        {formatNumber(comparisonData.comparison.difference)}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1 }}
                      >
                        Zmiana wartości średniej między okresami
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Data Points Comparison */}
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: "100%", bgcolor: "grey.100" }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Liczba Pomiarów
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Okres 1:
                          </Typography>
                          <Typography
                            variant="h4"
                            fontWeight="bold"
                            color="primary"
                          >
                            {comparisonData.comparison.period1_count}
                          </Typography>
                        </Box>
                        <Typography variant="h5" color="text.secondary">
                          vs
                        </Typography>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Okres 2:
                          </Typography>
                          <Typography
                            variant="h4"
                            fontWeight="bold"
                            color="secondary"
                          >
                            {comparisonData.comparison.period2_count}
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Paper>

            {/* Detailed Statistics Comparison */}
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Szczegółowe Statystyki
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                {/* Average Values */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={1} sx={{ p: 2, height: "100%" }}>
                    <Typography
                      variant="subtitle1"
                      fontWeight="bold"
                      gutterBottom
                      color="primary"
                    >
                      Wartości Średnie
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 2,
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 1:
                        </Typography>
                        <Typography variant="h5" fontWeight="bold">
                          {formatNumber(comparisonData.comparison.period1_avg)}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, textAlign: "right" }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 2:
                        </Typography>
                        <Typography variant="h5" fontWeight="bold">
                          {formatNumber(comparisonData.comparison.period2_avg)}
                        </Typography>
                      </Box>
                    </Box>
                    <Divider />
                    <Box
                      sx={{ mt: 2, p: 1, bgcolor: "grey.100", borderRadius: 1 }}
                    >
                      <Typography variant="body2" textAlign="center">
                        Różnica:{" "}
                        <strong>
                          {formatNumber(
                            Math.abs(
                              comparisonData.comparison.period2_avg -
                                comparisonData.comparison.period1_avg
                            )
                          )}
                        </strong>
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>

                {/* Median Values */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={1} sx={{ p: 2, height: "100%" }}>
                    <Typography
                      variant="subtitle1"
                      fontWeight="bold"
                      gutterBottom
                      color="primary"
                    >
                      Mediany
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 2,
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 1:
                        </Typography>
                        <Typography variant="h5" fontWeight="bold">
                          {formatNumber(
                            comparisonData.comparison.period1_median
                          )}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, textAlign: "right" }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 2:
                        </Typography>
                        <Typography variant="h5" fontWeight="bold">
                          {formatNumber(
                            comparisonData.comparison.period2_median
                          )}
                        </Typography>
                      </Box>
                    </Box>
                    <Divider />
                    <Box
                      sx={{ mt: 2, p: 1, bgcolor: "grey.100", borderRadius: 1 }}
                    >
                      <Typography variant="body2" textAlign="center">
                        Różnica:{" "}
                        <strong>
                          {formatNumber(
                            Math.abs(
                              comparisonData.comparison.period2_median -
                                comparisonData.comparison.period1_median
                            )
                          )}
                        </strong>
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>

                {/* Max Values */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={1} sx={{ p: 2, height: "100%" }}>
                    <Typography
                      variant="subtitle1"
                      fontWeight="bold"
                      gutterBottom
                      color="error"
                    >
                      Wartości Maksymalne
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 2,
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 1:
                        </Typography>
                        <Typography
                          variant="h5"
                          fontWeight="bold"
                          color="error"
                        >
                          {formatNumber(comparisonData.comparison.period1_max)}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, textAlign: "right" }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 2:
                        </Typography>
                        <Typography
                          variant="h5"
                          fontWeight="bold"
                          color="error"
                        >
                          {formatNumber(comparisonData.comparison.period2_max)}
                        </Typography>
                      </Box>
                    </Box>
                    <Divider />
                    <Box
                      sx={{ mt: 2, p: 1, bgcolor: "grey.100", borderRadius: 1 }}
                    >
                      <Typography variant="body2" textAlign="center">
                        {comparisonData.comparison.period2_max >
                        comparisonData.comparison.period1_max
                          ? "Wzrost maksimum"
                          : "Spadek maksimum"}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>

                {/* Min Values */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={1} sx={{ p: 2, height: "100%" }}>
                    <Typography
                      variant="subtitle1"
                      fontWeight="bold"
                      gutterBottom
                      color="success"
                    >
                      Wartości Minimalne
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 2,
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 1:
                        </Typography>
                        <Typography
                          variant="h5"
                          fontWeight="bold"
                          color="success"
                        >
                          {formatNumber(comparisonData.comparison.period1_min)}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, textAlign: "right" }}>
                        <Typography variant="body2" color="text.secondary">
                          Okres 2:
                        </Typography>
                        <Typography
                          variant="h5"
                          fontWeight="bold"
                          color="success"
                        >
                          {formatNumber(comparisonData.comparison.period2_min)}
                        </Typography>
                      </Box>
                    </Box>
                    <Divider />
                    <Box
                      sx={{ mt: 2, p: 1, bgcolor: "grey.100", borderRadius: 1 }}
                    >
                      <Typography variant="body2" textAlign="center">
                        {comparisonData.comparison.period2_min >
                        comparisonData.comparison.period1_min
                          ? "Wzrost minimum"
                          : "Spadek minimum"}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </Paper>

            {/* Summary Insight */}
            <Paper elevation={3} sx={{ p: 3, mb: 3, bgcolor: "info.light" }}>
              <Typography variant="h6" gutterBottom color="white">
                Podsumowanie Analizy
              </Typography>
              <Divider sx={{ mb: 2, borderColor: "white" }} />
              <Typography variant="body1" color="white" paragraph>
                {comparisonData.comparison.trend === "increasing" &&
                  `Zaobserwowano wzrost zużycia o ${formatNumber(
                    Math.abs(comparisonData.comparison.percentage_change)
                  )}%. 
                   Wartość średnia wzrosła z ${formatNumber(
                     comparisonData.comparison.period1_avg
                   )} do ${formatNumber(
                    comparisonData.comparison.period2_avg
                  )}, 
                   co stanowi bezwzględny wzrost o ${formatNumber(
                     comparisonData.comparison.difference
                   )} jednostek.`}
                {comparisonData.comparison.trend === "decreasing" &&
                  `Zaobserwowano spadek zużycia o ${formatNumber(
                    Math.abs(comparisonData.comparison.percentage_change)
                  )}%. 
                   Wartość średnia spadła z ${formatNumber(
                     comparisonData.comparison.period1_avg
                   )} do ${formatNumber(
                    comparisonData.comparison.period2_avg
                  )}, 
                   co stanowi bezwzględny spadek o ${formatNumber(
                     Math.abs(comparisonData.comparison.difference)
                   )} jednostek.`}
                {comparisonData.comparison.trend === "stable" &&
                  `Zużycie pozostało stabilne z minimalną zmianą ${formatNumber(
                    Math.abs(comparisonData.comparison.percentage_change)
                  )}%. 
                   Wartość średnia zmieniła się z ${formatNumber(
                     comparisonData.comparison.period1_avg
                   )} do ${formatNumber(
                    comparisonData.comparison.period2_avg
                  )}.`}
              </Typography>
              <Typography variant="body1" color="white">
                Analiza oparta na {comparisonData.comparison.period1_count}{" "}
                pomiarach w pierwszym okresie i{" "}
                {comparisonData.comparison.period2_count} pomiarach w drugim
                okresie.
              </Typography>
            </Paper>

            {/* Comparison Tables */}
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Tabela Porównawcza - Statystyki
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: "grey.200" }}>
                      <TableCell>
                        <strong>Metryka</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>Okres 1</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>Okres 2</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>Różnica</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>Zmiana %</strong>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Wartość Średnia</strong>
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period1_avg)}
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period2_avg)}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            comparisonData.comparison.difference > 0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {comparisonData.comparison.difference > 0 ? "+" : ""}
                        {formatNumber(comparisonData.comparison.difference)}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            comparisonData.comparison.percentage_change > 0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {comparisonData.comparison.percentage_change > 0
                          ? "+"
                          : ""}
                        {formatNumber(
                          comparisonData.comparison.percentage_change
                        )}
                        %
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Mediana</strong>
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period1_median)}
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period2_median)}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            comparisonData.comparison.period2_median -
                              comparisonData.comparison.period1_median >
                            0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {comparisonData.comparison.period2_median -
                          comparisonData.comparison.period1_median >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          comparisonData.comparison.period2_median -
                            comparisonData.comparison.period1_median
                        )}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            ((comparisonData.comparison.period2_median -
                              comparisonData.comparison.period1_median) /
                              comparisonData.comparison.period1_median) *
                              100 >
                            0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {((comparisonData.comparison.period2_median -
                          comparisonData.comparison.period1_median) /
                          comparisonData.comparison.period1_median) *
                          100 >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          ((comparisonData.comparison.period2_median -
                            comparisonData.comparison.period1_median) /
                            comparisonData.comparison.period1_median) *
                            100
                        )}
                        %
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Wartość Maksymalna</strong>
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period1_max)}
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period2_max)}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            comparisonData.comparison.period2_max -
                              comparisonData.comparison.period1_max >
                            0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {comparisonData.comparison.period2_max -
                          comparisonData.comparison.period1_max >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          comparisonData.comparison.period2_max -
                            comparisonData.comparison.period1_max
                        )}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            ((comparisonData.comparison.period2_max -
                              comparisonData.comparison.period1_max) /
                              comparisonData.comparison.period1_max) *
                              100 >
                            0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {((comparisonData.comparison.period2_max -
                          comparisonData.comparison.period1_max) /
                          comparisonData.comparison.period1_max) *
                          100 >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          ((comparisonData.comparison.period2_max -
                            comparisonData.comparison.period1_max) /
                            comparisonData.comparison.period1_max) *
                            100
                        )}
                        %
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Wartość Minimalna</strong>
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period1_min)}
                      </TableCell>
                      <TableCell align="center">
                        {formatNumber(comparisonData.comparison.period2_min)}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            comparisonData.comparison.period2_min -
                              comparisonData.comparison.period1_min >
                            0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {comparisonData.comparison.period2_min -
                          comparisonData.comparison.period1_min >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          comparisonData.comparison.period2_min -
                            comparisonData.comparison.period1_min
                        )}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{
                          color:
                            ((comparisonData.comparison.period2_min -
                              comparisonData.comparison.period1_min) /
                              comparisonData.comparison.period1_min) *
                              100 >
                            0
                              ? "error.main"
                              : "success.main",
                          fontWeight: "bold",
                        }}
                      >
                        {((comparisonData.comparison.period2_min -
                          comparisonData.comparison.period1_min) /
                          comparisonData.comparison.period1_min) *
                          100 >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          ((comparisonData.comparison.period2_min -
                            comparisonData.comparison.period1_min) /
                            comparisonData.comparison.period1_min) *
                            100
                        )}
                        %
                      </TableCell>
                    </TableRow>

                    <TableRow sx={{ bgcolor: "info.light" }}>
                      <TableCell component="th" scope="row">
                        <strong style={{ color: "white" }}>
                          Liczba Pomiarów
                        </strong>
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ color: "white", fontWeight: "bold" }}
                      >
                        {comparisonData.comparison.period1_count}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ color: "white", fontWeight: "bold" }}
                      >
                        {comparisonData.comparison.period2_count}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ color: "white", fontWeight: "bold" }}
                      >
                        {comparisonData.comparison.period2_count -
                          comparisonData.comparison.period1_count >
                        0
                          ? "+"
                          : ""}
                        {comparisonData.comparison.period2_count -
                          comparisonData.comparison.period1_count}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ color: "white", fontWeight: "bold" }}
                      >
                        {((comparisonData.comparison.period2_count -
                          comparisonData.comparison.period1_count) /
                          comparisonData.comparison.period1_count) *
                          100 >
                        0
                          ? "+"
                          : ""}
                        {formatNumber(
                          ((comparisonData.comparison.period2_count -
                            comparisonData.comparison.period1_count) /
                            comparisonData.comparison.period1_count) *
                            100
                        )}
                        %
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>

            {/* Additional Comparison Table - Periods Info */}
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Tabela Porównawcza - Informacje o Okresach
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: "grey.200" }}>
                      <TableCell>
                        <strong>Właściwość</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>Raport Pierwszy</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>Raport Drugi</strong>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>ID Raportu</strong>
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ fontFamily: "monospace", fontSize: "0.75rem" }}
                      >
                        {comparison.report_one?.report_id}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ fontFamily: "monospace", fontSize: "0.75rem" }}
                      >
                        {comparison.report_two?.report_id}
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Okres Danych</strong>
                      </TableCell>
                      <TableCell align="center">
                        {
                          comparison.report_one?.report_criteria
                            ?.date_created_from
                        }{" "}
                        do{" "}
                        {
                          comparison.report_one?.report_criteria
                            ?.date_created_to
                        }
                      </TableCell>
                      <TableCell align="center">
                        {
                          comparison.report_two?.report_criteria
                            ?.date_created_from
                        }{" "}
                        do{" "}
                        {
                          comparison.report_two?.report_criteria
                            ?.date_created_to
                        }
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Lokalizacja</strong>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={
                            comparison.report_one?.report_criteria?.location ||
                            "Wszystkie"
                          }
                          color="primary"
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={
                            comparison.report_two?.report_criteria?.location ||
                            "Wszystkie"
                          }
                          color="secondary"
                          size="small"
                        />
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Typ Urządzenia</strong>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={
                            comparison.report_one?.report_criteria
                              ?.device_type || "Wszystkie"
                          }
                          color="primary"
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={
                            comparison.report_two?.report_criteria
                              ?.device_type || "Wszystkie"
                          }
                          color="secondary"
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                    </TableRow>

                    <TableRow hover>
                      <TableCell component="th" scope="row">
                        <strong>Liczba Pomiarów</strong>
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ fontWeight: "bold", color: "primary.main" }}
                      >
                        {comparisonData?.report_one?.data_points || "N/A"}
                      </TableCell>
                      <TableCell
                        align="center"
                        sx={{ fontWeight: "bold", color: "secondary.main" }}
                      >
                        {comparisonData?.report_two?.data_points || "N/A"}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </>
        )}

        {/* Comparison Data - Only as fallback */}
        {comparisonData && !comparisonData.comparison && (
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Comparison Statistics
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Paper elevation={0} sx={{ p: 2, bgcolor: "grey.100" }}>
              <pre
                style={{
                  margin: 0,
                  fontFamily: "monospace",
                  fontSize: "0.875rem",
                  whiteSpace: "pre-wrap",
                  wordWrap: "break-word",
                }}
              >
                {JSON.stringify(comparisonData, null, 2)}
              </pre>
            </Paper>
          </Paper>
        )}

        {/* Visualization */}
        {comparison.visualization_file && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Comparison Visualization
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box sx={{ textAlign: "center" }}>
              <img
                src={analysisReportingApi.getVisualizationUrl(
                  comparison.visualization_file
                )}
                alt="Comparison Chart"
                style={{
                  maxWidth: "100%",
                  height: "auto",
                  display: "block",
                  margin: "0 auto",
                }}
                onError={(e) => {
                  e.target.style.display = "none";
                  e.target.nextSibling.style.display = "block";
                }}
              />
              <Typography
                variant="caption"
                color="error"
                sx={{ display: "none", mt: 2 }}
              >
                Failed to load visualization
              </Typography>
            </Box>
          </Paper>
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
    </Box>
  );
}

export default ComparisonDetailsPage;
