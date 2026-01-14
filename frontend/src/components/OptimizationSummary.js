import React, { useState, useEffect } from 'react';
import { optimizationApi } from '../api/optimizationApi';

export const OptimizationSummary = ({ data }) => {
  if (!data) return null;

  const summary = data.summary;
  const costs = data.costs;
  const energy = data.energy_distribution;

  const isSavings = costs.savings_pln > 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Podsumowanie Optymalizacji</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Urządzenia */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">Liczba urządzeń</p>
          <p className="text-3xl font-bold text-blue-600">{summary.devices_count}</p>
        </div>

        {/* Zapotrzebowanie */}
        <div className="bg-purple-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">Całkowite zapotrzebowanie</p>
          <p className="text-3xl font-bold text-purple-600">{summary.total_demand_kwh} kWh</p>
        </div>

        {/* Generacja */}
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">Wygenerowana energia</p>
          <p className="text-3xl font-bold text-green-600">{summary.generation_kwh} kWh</p>
        </div>

        {/* Bateria */}
        <div className="bg-orange-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">Stan baterii na początek</p>
          <p className="text-3xl font-bold text-orange-600">{summary.battery_start_kwh} kWh</p>
        </div>

        {/* Użyta bateria */}
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">Użyta bateria</p>
          <p className="text-3xl font-bold text-red-600">{summary.battery_used_kwh} kWh</p>
        </div>

        {/* Pozostała bateria */}
        <div className="bg-yellow-50 p-4 rounded-lg">
          <p className="text-gray-600 text-sm">Pozostała bateria</p>
          <p className="text-3xl font-bold text-yellow-600">{summary.battery_remaining_kwh} kWh</p>
        </div>
      </div>

      {/* Koszty */}
      <div className="border-t pt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Analiza Kosztów</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Koszt tradycyjny */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-600 text-sm">Koszt tradycyjny (bez optymalizacji)</p>
            <p className="text-3xl font-bold text-gray-800">{costs.reference_total_pln} PLN</p>
          </div>

          {/* Koszt zoptymalizowany */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-600 text-sm">Koszt zoptymalizowany</p>
            <p className="text-3xl font-bold text-gray-800">{costs.optimal_total_pln} PLN</p>
          </div>
        </div>

        {/* Oszczędności */}
        <div className={`p-4 rounded-lg ${isSavings ? 'bg-green-50' : 'bg-red-50'}`}>
          <p className={`text-sm ${isSavings ? 'text-green-600' : 'text-red-600'}`}>
            Oszczędności
          </p>
          <p className={`text-3xl font-bold ${isSavings ? 'text-green-600' : 'text-red-600'}`}>
            {costs.savings_pln} PLN ({costs.savings_percent}%)
          </p>
        </div>
      </div>

      {/* Rozkład energii */}
      <div className="border-t mt-6 pt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Rozkład Energii Sieciowej</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Scenariusz tradycyjny */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="font-semibold text-gray-800 mb-3">Tradycyjny (bez optymalizacji)</p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Energia nocna:</span>
                <span className="font-semibold">{energy.reference.night_kwh} kWh</span>
              </div>
              <div className="flex justify-between">
                <span>Energia dzienna:</span>
                <span className="font-semibold">{energy.reference.day_kwh} kWh</span>
              </div>
            </div>
          </div>

          {/* Scenariusz zoptymalizowany */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="font-semibold text-blue-900 mb-3">Zoptymalizowany</p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Energia nocna:</span>
                <span className="font-semibold">{energy.optimal.night_kwh} kWh</span>
              </div>
              <div className="flex justify-between">
                <span>Energia dzienna:</span>
                <span className="font-semibold">{energy.optimal.day_kwh} kWh</span>
              </div>
            </div>
          </div>
        </div>

        {/* Przesunięcie do nocy */}
        <div className="mt-4 p-4 bg-green-50 rounded-lg border-l-4 border-green-600">
          <p className="text-gray-600 text-sm">Przesunięcie energii do okresu nocnego</p>
          <p className="text-2xl font-bold text-green-600">
            +{energy.shift_to_night_kwh} kWh
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Więcej energii zaplanowanej na tańszy okres nocny
          </p>
        </div>
      </div>
    </div>
  );
};

export default OptimizationSummary;
