import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, CloudRain, AlertTriangle } from 'lucide-react';
import RiskMap from './components/RiskMap';
import WeatherSimulator from './components/WeatherSimulator';
import IncidentFeed from './components/IncidentFeed';

// Configure Axios
axios.defaults.baseURL = 'http://localhost:8000';

function App() {
  const [geoData, setGeoData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initial Fetch
  const fetchGridData = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/v1/grid/risk');
      setGeoData(res.data);
    } catch (error) {
      console.error("Failed to fetch grid risk data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGridData();
  }, []);

  return (
    <div className="flex flex-col h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header - Minimal, Professional */}
      <header className="flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200 shadow-sm z-20">
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold tracking-tight text-gray-800">
            DDMA GIS Command Dashboard
          </h1>
        </div>
        <div className="text-sm font-medium text-gray-500">
          Aizawl Corridor Sector
        </div>
      </header>

      {/* Main Content Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: GIS Map (Takes remaining width) */}
        <main className="flex-1 relative z-10">
          {loading && !geoData ? (
            <div className="flex items-center justify-center h-full">
              <span className="text-gray-500">Loading Map Data...</span>
            </div>
          ) : (
            <RiskMap geoData={geoData} />
          )}

          {/* Floating Weather Control Widget */}
          <div className="absolute bottom-6 left-6 z-[1000]">
            <WeatherSimulator onSimulationComplete={fetchGridData} />
          </div>
        </main>

        {/* Right Sidebar: Incident Feed (Fixed Width) */}
        <aside className="w-96 bg-white border-l border-gray-200 flex flex-col z-20 shadow-[-4px_0_15px_-3px_rgba(0,0,0,0.05)] overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              Live Incidents
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <IncidentFeed />
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;
