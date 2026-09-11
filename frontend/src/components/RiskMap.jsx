import React, { useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';

const RiskMap = ({ geoData }) => {
  // Aizawl center coordinates
  const center = [23.73, 92.71];

  // Dynamic styling based on ISRO ML risk threshold
  const getStyle = (feature) => {
    const risk = feature.properties.current_risk || 0;
    
    let color = '#22c55e'; // Green
    let fillOpacity = 0.35;
    
    if (risk >= 0.70) {
      color = '#ef4444'; // Red
      fillOpacity = 0.65;
    } else if (risk >= 0.40) {
      color = '#f97316'; // Orange
      fillOpacity = 0.50;
    }
    
    return {
      color: '#ffffff', // White stroke for crisp enterprise look
      weight: 1,
      fillColor: color,
      fillOpacity: fillOpacity
    };
  };

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const { grid_id, current_risk, base_slope, soil_porosity } = feature.properties;
      const risk = current_risk || 0;
      const slope = base_slope || 0;
      const porosity = soil_porosity || 0;
      
      const popupContent = `
        <div class="font-sans text-sm">
          <strong class="text-gray-900 block mb-1">Cell: ${grid_id}</strong>
          <table class="w-full text-left border-collapse">
            <tbody>
              <tr class="border-b border-gray-100">
                <td class="py-1 text-gray-500">Risk Score</td>
                <td class="py-1 font-semibold ${(risk >= 0.70) ? 'text-red-600' : 'text-gray-800'}">${(risk * 100).toFixed(2)}%</td>
              </tr>
              <tr class="border-b border-gray-100">
                <td class="py-1 text-gray-500">Base Slope</td>
                <td class="py-1 text-gray-800">${slope.toFixed(2)}°</td>
              </tr>
              <tr>
                <td class="py-1 text-gray-500">Soil Porosity</td>
                <td class="py-1 text-gray-800">${porosity.toFixed(2)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
      layer.bindPopup(popupContent);
    }
  };

  // Generate a unique key based on data content so React-Leaflet properly hydrates
  // the GeoJSON layer without triggering "Map already initialized" errors on updates.
  const geoKey = useMemo(() => {
    if (!geoData || !geoData.features) return 'empty';
    // Using sum of risk as a cheap hash to force re-render when risks change
    const riskSum = geoData.features.reduce((acc, f) => acc + (f.properties.current_risk || 0), 0);
    return `geo-${geoData.features.length}-${riskSum.toFixed(5)}`;
  }, [geoData]);

  if (!geoData) return null;

  return (
    <MapContainer 
      center={center} 
      zoom={13} 
      className="w-full h-full"
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        className="map-tiles"
      />
      <GeoJSON 
        key={geoKey}
        data={geoData} 
        style={getStyle} 
        onEachFeature={onEachFeature} 
      />
    </MapContainer>
  );
};

export default RiskMap;
