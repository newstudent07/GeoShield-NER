import React, { useState } from 'react';
import axios from 'axios';
import { CloudRain, RefreshCw } from 'lucide-react';

const WeatherSimulator = ({ onSimulationComplete }) => {
  const [rainfall, setRainfall] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  // Check 2: Throttled/Debounced actual API call triggered on drag-end.
  const handleDragEnd = async () => {
    setIsSimulating(true);
    try {
      await axios.post('/api/v1/simulate/weather', {
        rainfall_mm: parseFloat(rainfall)
      });
      if (onSimulationComplete) {
        await onSimulationComplete();
      }
    } catch (error) {
      console.error("Simulation failed", error);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-md w-80">
      <div className="flex items-center gap-2 mb-4">
        <CloudRain className="w-5 h-5 text-blue-500" />
        <h3 className="font-semibold text-gray-800">Weather Simulator</h3>
      </div>
      
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2 text-gray-600">
          <span>0 mm</span>
          <span className="font-bold text-blue-600">{rainfall} mm</span>
          <span>200 mm</span>
        </div>
        
        <input 
          type="range" 
          min="0" 
          max="200" 
          step="0.5"
          value={rainfall}
          onChange={(e) => setRainfall(e.target.value)}
          onMouseUp={handleDragEnd}
          onTouchEnd={handleDragEnd}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          disabled={isSimulating}
        />
      </div>

      <div className="flex items-center text-xs text-gray-500 bg-gray-50 p-2 rounded">
        {isSimulating ? (
          <><RefreshCw className="w-3 h-3 mr-2 animate-spin text-blue-500" /> Computing terrain risk...</>
        ) : (
          <>Drag slider and release to simulate rainfall impact.</>
        )}
      </div>
    </div>
  );
};

export default WeatherSimulator;
