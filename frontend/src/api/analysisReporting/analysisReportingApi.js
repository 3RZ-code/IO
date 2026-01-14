import api from "../axios";

const BASE_URL = "/analysis-reporting";

/**
 * API Service for Analysis & Reporting Module
 */
const analysisReportingApi = {
  // ============== REPORT CRITERIA ==============

  /**
   * Create new report criteria
   * @param {Object} criteriaData - { location, device_type, date_from, date_to }
   */
  createCriteria: async (criteriaData) => {
    const response = await api.post(`${BASE_URL}/criteria/`, criteriaData);
    return response.data;
  },

  /**
   * Get all report criteria
   */
  getAllCriteria: async () => {
    const response = await api.get(`${BASE_URL}/criteria/`);
    return response.data;
  },

  /**
   * Get single criteria by ID
   */
  getCriteriaById: async (criteriaId) => {
    const response = await api.get(`${BASE_URL}/criteria/${criteriaId}/`);
    return response.data;
  },

  /**
   * Update criteria
   */
  updateCriteria: async (criteriaId, criteriaData) => {
    const response = await api.patch(
      `${BASE_URL}/criteria/${criteriaId}/`,
      criteriaData
    );
    return response.data;
  },

  /**
   * Delete criteria
   */
  deleteCriteria: async (criteriaId) => {
    await api.delete(`${BASE_URL}/criteria/${criteriaId}/`);
  },

  // ============== REPORTS ==============

  /**
   * Generate new report
   * @param {Object} reportData - { criteria_id, generate_charts, use_ai }
   */
  generateReport: async (reportData) => {
    const response = await api.post(
      `${BASE_URL}/reports/generate/`,
      reportData
    );
    return response.data;
  },

  /**
   * Get all reports
   */
  getAllReports: async () => {
    const response = await api.get(`${BASE_URL}/reports/`);
    return response.data;
  },

  /**
   * Get reports by user ID
   */
  getReportsByUser: async (userId) => {
    const response = await api.get(
      `${BASE_URL}/reports/by_user/?user_id=${userId}`
    );
    return response.data;
  },

  /**
   * Get single report by ID
   */
  getReportById: async (reportId) => {
    const response = await api.get(`${BASE_URL}/reports/${reportId}/`);
    return response.data;
  },

  /**
   * Generate anomaly analysis for existing report
   * @param {string} reportId
   * @param {Object} options - { generate_chart, use_ai }
   */
  generateAnomalyAnalysis: async (reportId, options = {}) => {
    const response = await api.post(
      `${BASE_URL}/reports/${reportId}/generate_anomaly/`,
      options
    );
    return response.data;
  },

  /**
   * Export full report (JSON)
   */
  exportReport: async (reportId) => {
    const response = await api.get(`${BASE_URL}/reports/${reportId}/export/`);
    return response.data;
  },

  /**
   * Export only report data (JSON)
   */
  exportReportData: async (reportId) => {
    const response = await api.get(
      `${BASE_URL}/reports/${reportId}/export_data/`
    );
    return response.data;
  },

  /**
   * Export report as PDF
   * Downloads PDF file directly
   */
  exportReportPDF: async (reportId) => {
    const response = await api.get(
      `${BASE_URL}/reports/${reportId}/export_pdf/`,
      {
        responseType: "blob",
      }
    );

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `report_${reportId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return response.data;
  },

  /**
   * Update report
   */
  updateReport: async (reportId, reportData) => {
    const response = await api.patch(
      `${BASE_URL}/reports/${reportId}/`,
      reportData
    );
    return response.data;
  },

  /**
   * Delete report
   */
  deleteReport: async (reportId) => {
    await api.delete(`${BASE_URL}/reports/${reportId}/`);
  },

  // ============== ANALYSES ==============

  /**
   * Get all analyses
   */
  getAllAnalyses: async () => {
    const response = await api.get(`${BASE_URL}/analyses/`);
    return response.data;
  },

  /**
   * Get single analysis by ID
   */
  getAnalysisById: async (analysisId) => {
    const response = await api.get(`${BASE_URL}/analyses/${analysisId}/`);
    return response.data;
  },

  /**
   * Update analysis
   */
  updateAnalysis: async (analysisId, analysisData) => {
    const response = await api.patch(
      `${BASE_URL}/analyses/${analysisId}/`,
      analysisData
    );
    return response.data;
  },

  /**
   * Delete analysis
   */
  deleteAnalysis: async (analysisId) => {
    await api.delete(`${BASE_URL}/analyses/${analysisId}/`);
  },

  // ============== VISUALIZATIONS ==============

  /**
   * Get all visualizations
   */
  getAllVisualizations: async () => {
    const response = await api.get(`${BASE_URL}/visualizations/`);
    return response.data;
  },

  /**
   * Get single visualization by ID
   */
  getVisualizationById: async (visualizationId) => {
    const response = await api.get(
      `${BASE_URL}/visualizations/${visualizationId}/`
    );
    return response.data;
  },

  // ============== COMPARISONS ==============

  /**
   * Create comparison between two reports
   * @param {string} reportOneId
   * @param {string} reportTwoId
   */
  createComparison: async (reportOneId, reportTwoId) => {
    const response = await api.post(`${BASE_URL}/comparisons/compare/`, {
      report_one_id: reportOneId,
      report_two_id: reportTwoId,
    });
    return response.data;
  },

  /**
   * Get all comparisons
   */
  getAllComparisons: async () => {
    const response = await api.get(`${BASE_URL}/comparisons/`);
    return response.data;
  },

  /**
   * Get single comparison by ID
   */
  getComparisonById: async (comparisonId) => {
    const response = await api.get(`${BASE_URL}/comparisons/${comparisonId}/`);
    return response.data;
  },

  /**
   * Export comparison as PDF
   */
  exportComparisonPDF: async (comparisonId) => {
    const response = await api.get(
      `${BASE_URL}/comparisons/${comparisonId}/export_pdf/`,
      {
        responseType: "blob",
      }
    );

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `comparison_${comparisonId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return response.data;
  },

  /**
   * Delete comparison
   */
  deleteComparison: async (comparisonId) => {
    await api.delete(`${BASE_URL}/comparisons/${comparisonId}/`);
  },

  // ============== HELPER FUNCTIONS ==============

  /**
   * Get device metadata (locations and device types)
   */
  getDeviceMetadata: async () => {
    const response = await api.get(`${BASE_URL}/metadata/`);
    return response.data;
  },

  /**
   * Get available dates for selected criteria
   * @param {Object} params - { location?, device_type? }
   */
  getAvailableDates: async (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.location) queryParams.append("location", params.location);
    if (params.device_type)
      queryParams.append("device_type", params.device_type);

    const response = await api.get(
      `${BASE_URL}/available-dates/?${queryParams.toString()}`
    );
    return response.data;
  },

  /**
   * Get backend media URL for visualization file
   */
  getVisualizationUrl: (filePath) => {
    if (!filePath) return null;
    // File path already contains /media/charts/xxx.png from backend
    // Just prepend the base URL
    const baseURL = api.defaults.baseURL || "http://localhost:6543/";
    // Remove trailing slash from baseURL if present
    const cleanBaseURL = baseURL.endsWith("/") ? baseURL.slice(0, -1) : baseURL;
    // File path should start with /media/
    return `${cleanBaseURL}${filePath}`;
  },

  /**
   * Download JSON data as file
   */
  downloadJSON: (data, filename) => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export default analysisReportingApi;
