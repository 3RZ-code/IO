import React, { useState } from 'react';

export const OptimizationDatePicker = ({ onSubmit, isLoading }) => {
  const [useCustomDates, setUseCustomDates] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [errors, setErrors] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};

    if (useCustomDates) {
      if (!startDate) newErrors.startDate = 'Data początkowa jest wymagana';
      if (!endDate) newErrors.endDate = 'Data końcowa jest wymagana';

      if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        if (end <= start) {
          newErrors.dateRange = 'Data końcowa musi być później niż początkowa';
        }
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        return;
      }

      onSubmit(startDate, endDate);
      setStartDate('');
      setEndDate('');
    } else {
      onSubmit(null, null);
    }

    setErrors({});
  };

  const handleDefaultDates = () => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    start.setHours(0, 0, 0, 0);
    const end = new Date(start);
    end.setDate(end.getDate() + 1);

    setStartDate(start.toISOString().slice(0, 16));
    setEndDate(end.toISOString().slice(0, 16));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">⚙️ Optimalizacja Harmonogramu Urządzeń</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Toggle between default and custom dates */}
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              checked={!useCustomDates}
              onChange={() => {
                setUseCustomDates(false);
                setErrors({});
              }}
              className="w-4 h-4"
            />
            <span className="text-gray-700 font-medium">Następne 24 godziny (domyślnie)</span>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              checked={useCustomDates}
              onChange={() => {
                setUseCustomDates(true);
                handleDefaultDates();
              }}
              className="w-4 h-4"
            />
            <span className="text-gray-700 font-medium">Niestandardowy zakres dat</span>
          </label>
        </div>

        {/* Custom date inputs */}
        {useCustomDates && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data i godzina początkowa
              </label>
              <input
                type="datetime-local"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setErrors({ ...errors, startDate: '', dateRange: '' });
                }}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.startDate ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.startDate && (
                <p className="text-red-600 text-sm mt-1">{errors.startDate}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data i godzina końcowa
              </label>
              <input
                type="datetime-local"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setErrors({ ...errors, endDate: '', dateRange: '' });
                }}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.endDate ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.endDate && (
                <p className="text-red-600 text-sm mt-1">{errors.endDate}</p>
              )}
            </div>
          </div>
        )}

        {errors.dateRange && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {errors.dateRange}
          </div>
        )}

        {/* Submit button */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={isLoading}
            className={`flex-1 py-3 px-4 rounded-lg font-semibold text-white transition-colors ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
            }`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                Obliczanie...
              </span>
            ) : (
              <span>🚀 Oblicz Optymalizację</span>
            )}
          </button>
        </div>
      </form>

      {/* Info box */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
        <p className="text-sm text-gray-700">
          <strong>💡 Wskazówka:</strong> Algorytm optymalizacji analizuje harmonogram urządzeń,
          dostępną energię z baterii oraz taryfy czasowe, aby zaproponować najniższy koszt energii.
        </p>
      </div>
    </div>
  );
};

export default OptimizationDatePicker;
