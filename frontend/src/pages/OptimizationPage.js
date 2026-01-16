import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import HomeIcon from '@mui/icons-material/Home';
import AlarmIcon from '@mui/icons-material/Alarm';
import SettingsIcon from '@mui/icons-material/Settings';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import NotificationBell from '../components/NotificationBell';
import OptimizationDatePicker from '../components/OptimizationDatePicker';
import OptimizationSummary from '../components/OptimizationSummary';
import OptimizationScheduleTable from '../components/OptimizationScheduleTable';
import { optimizationApi } from '../api/optimizationApi';
import api from '../api/axios';

const OptimizationPage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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

  const handleOptimization = async (startDate, endDate) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      let response;
      if (startDate && endDate) {
        response = await optimizationApi.getOptimizationRecommendation(startDate, endDate);
      } else {
        response = await optimizationApi.getDefaultOptimization();
      }

      setData(response.data);
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        'Błąd podczas pobierania danych optymalizacji';
      setError(errorMsg);
      console.error('Optimization error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <SettingsSuggestIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Optimization & Control
          </Typography>
          <IconButton
            color="inherit"
            onClick={() => navigate("/")}
            sx={{ mr: 1 }}
            title="Strona główna"
          >
            <HomeIcon />
          </IconButton>
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

      <div className="min-h-screen bg-gray-100 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              🔋 Optymalizacja Harmonogramu Energii
            </h1>
            <p className="text-gray-600">
              Zaplanuj urządzenia w optymalnych godzinach, aby minimalizować koszty energii
            </p>
          </div>

        <OptimizationDatePicker onSubmit={handleOptimization} isLoading={loading} />

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 rounded-lg text-red-700">
            <p className="font-semibold">❌ Błąd</p>
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-block">
                <div className="animate-spin text-4xl mb-4">⚙️</div>
                <p className="text-gray-600 font-medium">Analizowanie danych...</p>
              </div>
            </div>
          </div>
        )}

        {data && !loading && (
          <>
            <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
              <p className="text-sm text-gray-600">
                <strong>Okres analizy:</strong>{' '}
                {new Date(data.window.start).toLocaleString('pl-PL')} -{' '}
                {new Date(data.window.end).toLocaleString('pl-PL')}
              </p>
            </div>

            <OptimizationSummary data={data} />

            <OptimizationScheduleTable
              schedules={{
                optimal: data.optimal_schedule,
                reference: data.reference_schedule,
              }}
            />

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">📋 Taryfy i Harmonogram</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Ceny Taryf</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between p-3 bg-blue-50 rounded">
                      <span className="text-gray-700">🌙 Taryfa nocna</span>
                      <span className="font-bold text-blue-600">
                        {data.tariffs.night_price_pln_per_kwh} PLN/kWh
                      </span>
                    </div>
                    <div className="flex justify-between p-3 bg-orange-50 rounded">
                      <span className="text-gray-700">☀️ Taryfa dzienna</span>
                      <span className="font-bold text-orange-600">
                        {data.tariffs.day_price_pln_per_kwh} PLN/kWh
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Harmonogram Taryf</h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>
                      <strong>Dzień roboczy:</strong>
                      <br />
                      {data.tariffs.schedule.weekday}
                    </p>
                    <p className="mt-3">
                      <strong>Weekend:</strong>
                      <br />
                      {data.tariffs.schedule.weekend}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {!data && !loading && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-gray-600 text-lg">
              Wciśnij przycisk powyżej, aby obliczyć optymalizację
            </p>
          </div>
        )}
      </div>
      </div>
    </Box>
  );
};

export default OptimizationPage;
