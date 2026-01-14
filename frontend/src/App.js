import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import PasswordResetRequestPage from "./pages/PasswordResetRequestPage";
import PasswordResetConfirmPage from "./pages/PasswordResetConfirmPage";
import DifficultLoginPage from "./pages/DifficultLoginPage";
import MainPage from "./pages/MainPage";
import UserProfilePage from "./pages/UserProfilePage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import TermsOfServicePage from "./pages/TermsOfServicePage";
import PrivacyPolicyPage from "./pages/PrivacyPolicyPage";
import AnalysisReportingPage from "./pages/analysisReporting";
import ReportDetailsPage from "./pages/analysisReporting/ReportDetailsPage";
import ComparisonDetailsPage from "./pages/analysisReporting/ComparisonDetailsPage";
import ProtectedRoute from "./components/ProtectedRoute";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/difficult-login" element={<DifficultLoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/password-reset" element={<PasswordResetRequestPage />} />
        <Route
          path="/password-reset/confirm"
          element={<PasswordResetConfirmPage />}
        />
        <Route path="/terms" element={<TermsOfServicePage />} />
        <Route path="/privacy" element={<PrivacyPolicyPage />} />

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<MainPage />} />
          <Route path="/profile" element={<UserProfilePage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route
            path="/analysis-reporting"
            element={<AnalysisReportingPage />}
          />
          <Route
            path="/analysis-reporting/report/:reportId"
            element={<ReportDetailsPage />}
          />
          <Route
            path="/analysis-reporting/comparison/:comparisonId"
            element={<ComparisonDetailsPage />}
          />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
