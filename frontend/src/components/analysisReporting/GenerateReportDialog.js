import { useState, useEffect, useCallback } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControlLabel,
  Checkbox,
  Box,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { pl } from "date-fns/locale";

/**
 * Component for creating report criteria and generating report
 */
function GenerateReportDialog({ open, onClose, onReportGenerated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState({ locations: [], device_types: [] });
  const [loadingMetadata, setLoadingMetadata] = useState(false);
  const [availableDates, setAvailableDates] = useState([]);
  const [loadingDates, setLoadingDates] = useState(false);

  const [formData, setFormData] = useState({
    location: "",
    device_type: "",
    date_from: null,
    date_to: null,
    generate_charts: true,
    use_ai: false,
  });

  useEffect(() => {
    if (open) {
      loadMetadata();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const loadAvailableDates = useCallback(async () => {
    setLoadingDates(true);
    try {
      const analysisReportingApi = (
        await import("../../api/analysisReporting/analysisReportingApi")
      ).default;

      const params = {};
      if (formData.location) params.location = formData.location;
      if (formData.device_type) params.device_type = formData.device_type;

      const data = await analysisReportingApi.getAvailableDates(params);
      setAvailableDates(data.dates || []);
    } catch (err) {
      console.error("Error loading available dates:", err);
      setAvailableDates([]);
    } finally {
      setLoadingDates(false);
    }
  }, [formData.location, formData.device_type]);

  useEffect(() => {
    // Load available dates when location or device_type changes
    if (open && (formData.location || formData.device_type)) {
      loadAvailableDates();
    }
  }, [open, formData.location, formData.device_type, loadAvailableDates]);

  const loadMetadata = async () => {
    setLoadingMetadata(true);
    try {
      const analysisReportingApi = (
        await import("../../api/analysisReporting/analysisReportingApi")
      ).default;
      const data = await analysisReportingApi.getDeviceMetadata();
      setMetadata(data);
    } catch (err) {
      console.error("Error loading metadata:", err);
      // Nie pokazuj błędu - użytkownik może wpisać ręcznie
    } finally {
      setLoadingMetadata(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);

    try {
      // Import here to avoid circular dependencies
      const analysisReportingApi = (
        await import("../../api/analysisReporting/analysisReportingApi")
      ).default;

      // Create criteria
      const criteriaData = {
        location: formData.location === "" ? null : formData.location,
        device_type: formData.device_type === "" ? null : formData.device_type,
        date_from: formData.date_from
          ? new Date(formData.date_from).toISOString().split("T")[0]
          : null,
        date_to: formData.date_to
          ? new Date(formData.date_to).toISOString().split("T")[0]
          : null,
        date_created_from: formData.date_from
          ? new Date(formData.date_from).toISOString().split("T")[0]
          : null,
        date_created_to: formData.date_to
          ? new Date(formData.date_to).toISOString().split("T")[0]
          : null,
      };

      const criteria = await analysisReportingApi.createCriteria(criteriaData);

      // Generate report
      const reportData = {
        criteria_id: criteria.report_criteria_id,
        generate_charts: formData.generate_charts,
        use_ai: formData.use_ai,
      };

      const report = await analysisReportingApi.generateReport(reportData);

      // Call parent callback
      if (onReportGenerated) {
        onReportGenerated(report);
      }

      // Reset form and close
      setFormData({
        location: "",
        device_type: "",
        date_from: null,
        date_to: null,
        generate_charts: true,
        use_ai: false,
      });
      setAvailableDates([]);
      onClose();
    } catch (err) {
      console.error("Error generating report:", err);
      setError(
        err.response?.data?.error ||
          err.response?.data?.message ||
          "Failed to generate report. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setError(null);
      onClose();
    }
  };

  const isFormValid = formData.date_from && formData.date_to;

  const shouldHighlightDay = (date) => {
    if (!date || availableDates.length === 0) return false;
    const dateStr = new Date(date).toISOString().split("T")[0];
    return availableDates.includes(dateStr);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Generate New Report</DialogTitle>
      <DialogContent>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <FormControl fullWidth disabled={loading || loadingMetadata}>
            <InputLabel>Location</InputLabel>
            <Select
              name="location"
              value={formData.location}
              label="Location"
              onChange={handleChange}
            >
              <MenuItem value="">
                <em>All locations</em>
              </MenuItem>
              {metadata.locations.map((loc) => (
                <MenuItem key={loc} value={loc}>
                  {loc}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth disabled={loading || loadingMetadata}>
            <InputLabel>Device Type</InputLabel>
            <Select
              name="device_type"
              value={formData.device_type}
              label="Device Type"
              onChange={handleChange}
            >
              <MenuItem value="">
                <em>All device types</em>
              </MenuItem>
              {metadata.device_types.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={pl}>
            <DatePicker
              label="Data od"
              value={formData.date_from}
              onChange={(newValue) =>
                setFormData((prev) => ({ ...prev, date_from: newValue }))
              }
              disabled={loading || loadingDates}
              shouldDisableDate={(date) => !shouldHighlightDay(date)}
              slotProps={{
                textField: {
                  fullWidth: true,
                  required: true,
                },
                day: {
                  sx: (ownerState) => ({
                    ...(shouldHighlightDay(ownerState.day) && {
                      backgroundColor: "primary.light",
                      color: "primary.contrastText",
                      "&:hover": {
                        backgroundColor: "primary.main",
                      },
                    }),
                  }),
                },
              }}
            />
          </LocalizationProvider>

          <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={pl}>
            <DatePicker
              label="Data do"
              value={formData.date_to}
              onChange={(newValue) =>
                setFormData((prev) => ({ ...prev, date_to: newValue }))
              }
              disabled={loading || loadingDates}
              shouldDisableDate={(date) => !shouldHighlightDay(date)}
              minDate={formData.date_from}
              slotProps={{
                textField: {
                  fullWidth: true,
                  required: true,
                },
                day: {
                  sx: (ownerState) => ({
                    ...(shouldHighlightDay(ownerState.day) && {
                      backgroundColor: "primary.light",
                      color: "primary.contrastText",
                      "&:hover": {
                        backgroundColor: "primary.main",
                      },
                    }),
                  }),
                },
              }}
            />
          </LocalizationProvider>

          <FormControlLabel
            control={
              <Checkbox
                name="generate_charts"
                checked={formData.generate_charts}
                onChange={handleChange}
                disabled={loading}
              />
            }
            label="Generate charts and visualizations"
          />

          <FormControlLabel
            control={
              <Checkbox
                name="use_ai"
                checked={formData.use_ai}
                onChange={handleChange}
                disabled={loading}
              />
            }
            label="Use AI for analysis summaries (takes longer)"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!isFormValid || loading}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? "Generating..." : "Generate Report"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default GenerateReportDialog;
