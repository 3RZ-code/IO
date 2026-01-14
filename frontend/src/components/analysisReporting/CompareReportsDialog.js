import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Typography,
} from "@mui/material";

/**
 * Dialog for comparing two reports
 */
function CompareReportsDialog({
  open,
  onClose,
  reports,
  selectedReport,
  onComparisonCreated,
}) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reportToCompare, setReportToCompare] = useState("");

  const handleCompare = async () => {
    if (!selectedReport || !reportToCompare) {
      setError("Please select both reports to compare");
      return;
    }

    if (selectedReport.report_id === reportToCompare) {
      setError("Cannot compare a report with itself");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const analysisReportingApi = (
        await import("../../api/analysisReporting/analysisReportingApi")
      ).default;

      const comparison = await analysisReportingApi.createComparison(
        selectedReport.report_id,
        reportToCompare
      );

      console.log("Comparison response:", comparison);
      console.log("report_compare_id:", comparison?.report_compare_id);

      if (onComparisonCreated) {
        onComparisonCreated(comparison);
      }

      setReportToCompare("");
      onClose();

      // Navigate to comparison details page
      navigate(
        `/analysis-reporting/comparison/${comparison.report_compare_id}`
      );
    } catch (err) {
      console.error("Error creating comparison:", err);
      setError(
        err.response?.data?.error ||
          err.response?.data?.message ||
          "Failed to create comparison"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setError(null);
      setReportToCompare("");
      onClose();
    }
  };

  // Filter out the selected report from options
  const availableReports = reports.filter(
    (r) => r.report_id !== selectedReport?.report_id
  );

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Compare Reports</DialogTitle>
      <DialogContent>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {selectedReport && (
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Comparing:
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: "bold" }}>
                Report from {selectedReport.report_criteria?.date_created_from}{" "}
                to {selectedReport.report_criteria?.date_created_to}
              </Typography>
            </Box>
          )}

          <FormControl fullWidth disabled={loading}>
            <InputLabel>Select Report to Compare With</InputLabel>
            <Select
              value={reportToCompare}
              label="Select Report to Compare With"
              onChange={(e) => setReportToCompare(e.target.value)}
            >
              {availableReports.length === 0 ? (
                <MenuItem disabled>No other reports available</MenuItem>
              ) : (
                availableReports.map((report) => (
                  <MenuItem key={report.report_id} value={report.report_id}>
                    Report: {report.report_criteria?.date_created_from} -{" "}
                    {report.report_criteria?.date_created_to}
                    {report.report_criteria?.location &&
                      ` | ${report.report_criteria.location}`}
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleCompare}
          variant="contained"
          disabled={!reportToCompare || loading}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? "Comparing..." : "Compare"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default CompareReportsDialog;
