import React, { useState } from 'react';
import OptimizationDatePicker from '../components/OptimizationDatePicker';
import OptimizationSummary from '../components/OptimizationSummary';
import OptimizationScheduleTable from '../components/OptimizationScheduleTable';
import { optimizationApi } from '../api/optimizationApi';

const OptimizationPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastQuery, setLastQuery] = useState(null);

  const handleOptimization = async (startDate, endDate) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      let response;
      if (startDate && endDate) {
        response = await optimizationApi.getOptimizationRecommendation(startDate, endDate);
        setLastQuery({ startDate, endDate });
      } else {
        response = await optimizationApi.getDefaultOptimization();
        const now = new Date();
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        start.setHours(0, 0, 0, 0);
        const end = new Date(start);
        end.setDate(end.getDate() + 1);
        setLastQuery({ startDate: start.toISOString(), endDate: end.toISOString() });
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
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🔋 Optymalizacja Harmonogramu Energii
          </h1>
          <p className="text-gray-600">
            Zaplanuj urządzenia w optymalnych godzinach, aby minimalizować koszty energii
          </p>
        </div>

        {/* Date Picker Form */}
        <OptimizationDatePicker onSubmit={handleOptimization} isLoading={loading} />

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 rounded-lg text-red-700">
            <p className="font-semibold">❌ Błąd</p>
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
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

        {/* Results */}
        {data && !loading && (
          <>
            {/* Time Window Info */}
            <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
              <p className="text-sm text-gray-600">
                <strong>Okres analizy:</strong>{' '}
                {new Date(data.window.start).toLocaleString('pl-PL')} -{' '}
                {new Date(data.window.end).toLocaleString('pl-PL')}
              </p>
            </div>

            {/* Summary */}
            <OptimizationSummary data={data} />

            {/* Schedule Tables */}
            <OptimizationScheduleTable
              schedules={{
                optimal: data.optimal_schedule,
                reference: data.reference_schedule,
              }}
            />

            {/* Tariff Information */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">📋 Taryfy i Harmonogram</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Tariff Prices */}
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

                {/* Schedule Information */}
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

        {/* Empty State */}
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
  );
};

export default OptimizationPage;
