import React, { useState } from 'react';

export const OptimizationScheduleTable = ({ schedules }) => {
  const [activeTab, setActiveTab] = useState('optimal');

  if (!schedules) return null;

  const schedule = activeTab === 'optimal' ? schedules.optimal : schedules.reference;
  const title = activeTab === 'optimal' ? 'Harmonogram Zoptymalizowany' : 'Harmonogram Tradycyjny';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">{title}</h2>

      {/* Tabbed Navigation */}
      <div className="flex gap-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('optimal')}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'optimal'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📊 Zoptymalizowany
        </button>
        <button
          onClick={() => setActiveTab('reference')}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'reference'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📈 Tradycyjny (kontrolny)
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b-2 border-gray-300">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-800">Urządzenie</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Priorytet</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Moc (kW)</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Czas</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Taryfa</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Energia (kWh)</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Z Baterii (kWh)</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Z Sieci (kWh)</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-800">Koszt (PLN)</th>
            </tr>
          </thead>
          <tbody>
            {schedule.map((item, idx) => {
              const startTime = new Date(item.start).toLocaleTimeString('pl-PL', {
                hour: '2-digit',
                minute: '2-digit',
              });
              const endTime = new Date(item.end).toLocaleTimeString('pl-PL', {
                hour: '2-digit',
                minute: '2-digit',
              });
              const isTariff = item.tariff === 'night';

              return (
                <tr
                  key={idx}
                  className={`border-b ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                  } hover:bg-blue-50 transition-colors`}
                >
                  <td className="px-4 py-3 font-medium text-gray-800">{item.device_name}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="inline-block px-2 py-1 bg-gray-200 rounded text-xs font-semibold">
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-700">{item.power_kw}</td>
                  <td className="px-4 py-3 text-center text-gray-700">
                    {startTime} - {endTime}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-3 py-1 rounded font-semibold text-white ${
                        isTariff
                          ? 'bg-blue-500'
                          : 'bg-orange-500'
                      }`}
                    >
                      {item.tariff === 'night' ? '🌙 Nocna' : '☀️ Dzienna'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-700">{item.energy_kwh}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-green-600 font-semibold">{item.battery_used_kwh}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-red-600 font-semibold">{item.grid_energy_kwh}</span>
                  </td>
                  <td className="px-4 py-3 text-center font-semibold text-gray-800">
                    {item.cost_pln} PLN
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg text-xs text-gray-600">
        <p className="font-semibold mb-2">Legenda:</p>
        <ul className="list-disc list-inside space-y-1">
          <li><span className="text-blue-600">Z Baterii</span> - energia pochodząca z systemu magazynowania</li>
          <li><span className="text-red-600">Z Sieci</span> - energia pobierana z sieci elektrycznej</li>
          <li><span className="text-blue-500">🌙 Nocna</span> - okres tańszy (0.6036 PLN/kWh)</li>
          <li><span className="text-orange-500">☀️ Dzienna</span> - okres droższy (0.6212 PLN/kWh)</li>
        </ul>
      </div>
    </div>
  );
};

export default OptimizationScheduleTable;
