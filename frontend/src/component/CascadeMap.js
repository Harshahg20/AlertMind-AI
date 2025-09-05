import React from "react";

const CascadeMap = ({ predictions, clients, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const highRiskPredictions = predictions.filter(
    (p) => p.prediction_confidence > 0.7
  );
  const mediumRiskPredictions = predictions.filter(
    (p) => p.prediction_confidence >= 0.5 && p.prediction_confidence <= 0.7
  );

  const getUrgencyLevel = (timeToCancel) => {
    if (timeToCancel <= 5)
      return {
        level: "IMMEDIATE",
        color: "text-red-400",
        bg: "bg-red-900/20",
      };
    if (timeToCancel <= 15)
      return {
        level: "URGENT",
        color: "text-orange-400",
        bg: "bg-orange-900/20",
      };
    if (timeToCancel <= 30)
      return {
        level: "MEDIUM",
        color: "text-yellow-400",
        bg: "bg-yellow-900/20",
      };
    return { level: "LOW", color: "text-green-400", bg: "bg-green-900/20" };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white flex items-center mb-2">
          <span className="mr-2">🔗</span>
          Cascade Prediction Map
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          AI-powered cascade failure predictions across your client
          infrastructure
        </p>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-red-900/20 rounded border border-red-500/20">
            <div className="text-lg font-bold text-red-400">
              {highRiskPredictions.length}
            </div>
            <div className="text-xs text-gray-400">High Risk</div>
          </div>
          <div className="text-center p-3 bg-yellow-900/20 rounded border border-yellow-500/20">
            <div className="text-lg font-bold text-yellow-400">
              {mediumRiskPredictions.length}
            </div>
            <div className="text-xs text-gray-400">Medium Risk</div>
          </div>
          <div className="text-center p-3 bg-blue-900/20 rounded border border-blue-500/20">
            <div className="text-lg font-bold text-blue-400">
              {predictions.length}
            </div>
            <div className="text-xs text-gray-400">Total Predictions</div>
          </div>
          <div className="text-center p-3 bg-purple-900/20 rounded border border-purple-500/20">
            <div className="text-lg font-bold text-purple-400">
              {predictions.reduce(
                (acc, p) => acc + p.predicted_cascade_systems.length,
                0
              )}
            </div>
            <div className="text-xs text-gray-400">Systems at Risk</div>
          </div>
        </div>
      </div>

      {/* High Priority Cascade Alerts */}
      {highRiskPredictions.length > 0 && (
        <div className="bg-gradient-to-r from-red-900/20 to-orange-900/20 border border-red-500/30 rounded-lg p-6">
          <h3 className="text-lg font-bold text-red-400 flex items-center mb-4">
            <span className="mr-2">🚨</span>
            IMMEDIATE ACTION REQUIRED
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {highRiskPredictions.slice(0, 4).map((prediction) => {
              const client = clients.find((c) => c.id === prediction.client_id);
              const urgency = getUrgencyLevel(
                prediction.time_to_cascade_minutes
              );

              return (
                <div
                  key={prediction.alert_id}
                  className="bg-gray-800/50 rounded-lg p-4 border border-red-500/30"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <span className="text-white font-medium">
                        {client ? client.name : "Unknown Client"}
                      </span>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded ${urgency.bg} ${urgency.color}`}
                    >
                      {urgency.level}
                    </span>
                  </div>
                  <div className="text-sm text-gray-300 mb-2">
                    {Math.round(prediction.prediction_confidence * 100)}%
                    confidence • {prediction.time_to_cascade_minutes} min
                  </div>
                  <div className="text-xs text-gray-400">
                    Systems at risk:{" "}
                    {prediction.predicted_cascade_systems.join(", ")}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Medium Priority */}
      {mediumRiskPredictions.length > 0 && (
        <div className="bg-gradient-to-r from-blue-900/20 to-yellow-900/20 border border-yellow-500/30 rounded-lg p-6">
          <h3 className="text-lg font-bold text-yellow-400 flex items-center mb-4">
            <span className="mr-2">⚠️</span>
            MEDIUM PRIORITY
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {mediumRiskPredictions.slice(0, 4).map((prediction) => {
              const client = clients.find((c) => c.id === prediction.client_id);
              return (
                <div
                  key={prediction.alert_id}
                  className="bg-gray-800/50 rounded-lg p-4 border border-yellow-500/30"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span className="text-white font-medium">
                        {client ? client.name : "Unknown Client"}
                      </span>
                    </div>
                    <span className="px-2 py-1 text-xs rounded bg-yellow-900/20 text-yellow-400">
                      MEDIUM
                    </span>
                  </div>
                  <div className="text-sm text-gray-300 mb-2">
                    {Math.round(prediction.prediction_confidence * 100)}%
                    confidence • {prediction.time_to_cascade_minutes} min
                  </div>
                  <div className="text-xs text-gray-400">
                    Systems at risk:{" "}
                    {prediction.predicted_cascade_systems.join(", ")}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default CascadeMap;
