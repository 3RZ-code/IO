import { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Grid,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import DeleteIcon from "@mui/icons-material/Delete";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import DownloadIcon from "@mui/icons-material/Download";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";

/**
 * Card component displaying single report in list
 */
function ReportCard({ report, onView, onDelete, onExport, onCompare }) {
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

  const getAnalysisTypes = () => {
    if (!report.analyses || report.analyses.length === 0) return [];
    return report.analyses.map((a) => a.analysis_type);
  };

  const criteria = report.report_criteria || {};
  const analysisTypes = getAnalysisTypes();

  return (
    <Card
      elevation={3}
      sx={{
        transition: "transform 0.2s, box-shadow 0.2s",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: "0 8px 24px rgba(33, 150, 243, 0.18)",
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
          <Typography variant="h6" component="div" noWrap>
            Report
          </Typography>
          <Box>
            <Tooltip title="View Details">
              <IconButton
                size="small"
                color="primary"
                onClick={() => onView(report)}
              >
                <VisibilityIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as PDF">
              <IconButton
                size="small"
                color="error"
                onClick={() => onExport(report.report_id, "pdf")}
              >
                <PictureAsPdfIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as JSON">
              <IconButton
                size="small"
                color="success"
                onClick={() => onExport(report.report_id, "json")}
              >
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Compare with another report">
              <IconButton
                size="small"
                color="info"
                onClick={() => onCompare(report)}
              >
                <CompareArrowsIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Report">
              <IconButton
                size="small"
                color="error"
                onClick={() => onDelete(report.report_id)}
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {report.report_description || "No description"}
        </Typography>

        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6}>
            <Typography variant="caption" color="text.secondary">
              Created:
            </Typography>
            <Typography variant="body2">
              {formatDate(report.created_timestamp)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="caption" color="text.secondary">
              Period:
            </Typography>
            <Typography variant="body2">
              {criteria.date_created_from} - {criteria.date_created_to}
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 1 }}>
          {criteria.location && (
            <Chip label={`📍 ${criteria.location}`} size="small" />
          )}
          {criteria.device_type && (
            <Chip label={`🔧 ${criteria.device_type}`} size="small" />
          )}
        </Box>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {analysisTypes.map((type, idx) => (
            <Chip
              key={idx}
              label={type}
              size="small"
              color={
                type === "TRENDS"
                  ? "primary"
                  : type === "PEAK"
                  ? "warning"
                  : "error"
              }
              variant="outlined"
            />
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}

export default ReportCard;
