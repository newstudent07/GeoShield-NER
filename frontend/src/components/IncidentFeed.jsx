import React from 'react';
import { Camera, CheckCircle, Clock } from 'lucide-react';

const IncidentFeed = () => {
  // Using static placeholder data as offline reports DB population is handled by Member 6
  // This satisfies the visual layout requirements.
  const incidents = [
    {
      id: "REP-1992",
      time: "10 mins ago",
      status: "Verified Hazard",
      confidence: 0.94,
      desc: "Deep fissure observed on NH-29 bend.",
      color: "text-red-600",
      bg: "bg-red-50"
    },
    {
      id: "REP-1991",
      time: "1 hour ago",
      status: "Clean Road",
      confidence: 0.88,
      desc: "Routine patrol image.",
      color: "text-green-600",
      bg: "bg-green-50"
    },
    {
      id: "REP-1990",
      time: "2 hours ago",
      status: "Pending Review",
      confidence: 0.65,
      desc: "Minor debris flow from recent rain.",
      color: "text-orange-600",
      bg: "bg-orange-50"
    }
  ];

  return (
    <div className="space-y-4">
      {incidents.map((incident) => (
        <div key={incident.id} className="border border-gray-100 rounded-md p-3 hover:shadow-sm transition-shadow bg-white">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-semibold text-gray-500 flex items-center gap-1">
              <Camera className="w-3 h-3" />
              {incident.id}
            </span>
            <span className="text-[10px] text-gray-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {incident.time}
            </span>
          </div>
          
          <p className="text-sm text-gray-700 mb-3">{incident.desc}</p>
          
          <div className="flex justify-between items-center text-xs">
            <span className={`px-2 py-1 rounded-full font-medium ${incident.color} ${incident.bg}`}>
              {incident.status}
            </span>
            <span className="text-gray-500 font-mono">
              AI: {(incident.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      ))}

      <div className="text-center pt-4">
        <p className="text-xs text-gray-400">Waiting for offline sync batches...</p>
      </div>
    </div>
  );
};

export default IncidentFeed;
