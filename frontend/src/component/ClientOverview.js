import React, { useState } from "react";

const ClientOverview = ({ clients, alerts, predictions, loading }) => {
  const [selectedClient, setSelectedClient] = useState(null);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const getClientStats = (clientId) => {
    const clientAlerts = alerts.filter((alert) => alert.client_id === clientId);
    const clientPredictions = predictions.filter(
      (pred) => pred.client_id === clientId
    );

    return {
      totalAlerts: clientAlerts.length,
      criticalAlerts: clientAlerts.filter((a) => a.severity === "critical")
        .length,
      warningAlerts: clientAlerts.filter((a) => a.severity === "warning")
        .length,
      predictions: clientPredictions.length,
      highRiskPredictions: clientPredictions.filter(
        (p) => p.prediction_confidence > 0.7
      ).length,
      avgCascadeRisk:
        clientAlerts.length > 0
          ? clientAlerts.reduce((acc, a) => acc + a.cascade_risk, 0) /
            clientAlerts.length
          : 0,
    };
  };

  const getTierColor = (tier) => {
    switch (tier.toLowerCase()) {
      case "enterprise":
        return "from-purple-500 to-purple-700";
      case "premium":
        return "from-blue-500 to-blue-700";
      case "standard":
        return "from-green-500 to-green-700";
      default:
        return "from-gray-500 to-gray-700";
    }
  };

  const getTierIcon = (tier) => {
    switch (tier.toLowerCase()) {
      case "enterprise":
        return "👑";
      case "premium":
        return "💎";
      case "standard":
        return "⭐";
      default:
        return "🏢";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white flex items-center mb-2">
          <span className="mr-2">👥</span>
          Client Overview
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          Monitor all your clients' IT infrastructure health and cascade
          predictions
        </p>

        {/* Overall Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-blue-900/20 rounded border border-blue-500/20">
            <div className="text-lg font-bold text-blue-400">
              {clients.length}
            </div>
            <div className="text-xs text-gray-400">Total Clients</div>
          </div>
          <div className="text-center p-3 bg-red-900/20 rounded border border-red-500/20">
            <div className="text-lg font-bold text-red-400">
              {alerts.filter((a) => a.severity === "critical").length}
            </div>
            <div className="text-xs text-gray-400">Critical Alerts</div>
          </div>
          <div className="text-center p-3 bg-yellow-900/20 rounded border border-yellow-500/20">
            <div className="text-lg font-bold text-yellow-400">
              {predictions.length}
            </div>
            <div className="text-xs text-gray-400">Active Predictions</div>
          </div>
          <div className="text-center p-3 bg-green-900/20 rounded border border-green-500/20">
            <div className="text-lg font-bold text-green-400">
              {
                clients.filter((c) => getClientStats(c.id).criticalAlerts === 0)
                  .length
              }
            </div>
            <div className="text-xs text-gray-400">Healthy Clients</div>
          </div>
        </div>
      </div>

      {/* Client Cards Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {clients.map((client) => {
          const stats = getClientStats(client.id);
          const hasIssues =
            stats.criticalAlerts > 0 || stats.highRiskPredictions > 0;

          return (
            <div
              key={client.id}
              className={`bg-gray-800 rounded-lg border transition-all hover:shadow-lg cursor-pointer ${
                hasIssues
                  ? "border-red-500/30 bg-red-900/5"
                  : "border-gray-700 hover:border-gray-600"
              }`}
              onClick={() => setSelectedClient(client)}
            >
              {/* Client Header */}
              <div className="p-4 border-b border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{getTierIcon(client.tier)}</span>
                    <h3 className="font-semibold text-white">{client.name}</h3>
                  </div>
                  <div
                    className={`px-2 py-1 text-xs rounded-full bg-gradient-to-r ${getTierColor(
                      client.tier
                    )} text-white`}
                  >
                    {client.tier}
                  </div>
                </div>

                <div className="text-sm text-gray-400">
                  <div className="flex items-center space-x-2 mb-1">
                    <span>🏗️</span>
                    <span>{client.environment}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>⏰</span>
                    <span>{client.business_hours}</span>
                  </div>
                </div>
              </div>

              {/* Alert Status */}
              <div className="p-4">
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="text-center p-2 bg-gray-700/30 rounded">
                    <div className="text-lg font-bold text-red-400">
                      {stats.criticalAlerts}
                    </div>
                    <div className="text-xs text-gray-400">Critical</div>
                  </div>
                  <div className="text-center p-2 bg-gray-700/30 rounded">
                    <div className="text-lg font-bold text-yellow-400">
                      {stats.warningAlerts}
                    </div>
                    <div className="text-xs text-gray-400">Warning</div>
                  </div>
                </div>

                {/* Cascade Risk Indicator */}
                <div className="mb-3">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-400">Cascade Risk</span>
                    <span
                      className={`font-semibold ${
                        stats.avgCascadeRisk > 0.7
                          ? "text-red-400"
                          : stats.avgCascadeRisk > 0.4
                          ? "text-yellow-400"
                          : "text-green-400"
                      }`}
                    >
                      {Math.round(stats.avgCascadeRisk * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        stats.avgCascadeRisk > 0.7
                          ? "bg-red-500"
                          : stats.avgCascadeRisk > 0.4
                          ? "bg-yellow-500"
                          : "bg-green-500"
                      }`}
                      style={{ width: `${stats.avgCascadeRisk * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Predictions Status */}
                {stats.predictions > 0 && (
                  <div className="p-2 bg-blue-900/20 border border-blue-500/20 rounded">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-blue-400">Active Predictions</span>
                      <span className="text-white font-semibold">
                        {stats.predictions}
                      </span>
                    </div>
                    {stats.highRiskPredictions > 0 && (
                      <div className="text-xs text-orange-400 mt-1">
                        🚨 {stats.highRiskPredictions} high-risk cascades
                      </div>
                    )}
                  </div>
                )}

                {/* Critical Systems */}
                <div className="mt-3">
                  <div className="text-xs text-gray-400 mb-1">
                    Critical Systems:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {client.critical_systems.slice(0, 3).map((system) => (
                      <span
                        key={system}
                        className="px-2 py-1 bg-gray-700 text-xs text-gray-300 rounded"
                      >
                        {system}
                      </span>
                    ))}
                    {client.critical_systems.length > 3 && (
                      <span className="px-2 py-1 bg-gray-600 text-xs text-gray-400 rounded">
                        +{client.critical_systems.length - 3}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Status Footer */}
              <div
                className={`px-4 py-2 border-t ${
                  hasIssues
                    ? "border-red-500/20 bg-red-900/10"
                    : "border-gray-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        hasIssues ? "bg-red-500 animate-pulse" : "bg-green-500"
                      }`}
                    ></div>
                    <span
                      className={`text-xs ${
                        hasIssues ? "text-red-400" : "text-green-400"
                      }`}
                    >
                      {hasIssues ? "Attention Required" : "All Systems Normal"}
                    </span>
                  </div>
                  <button className="text-xs text-blue-400 hover:text-blue-300">
                    View Details →
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Client Detail Modal */}
      {selectedClient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg border border-gray-600 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-600">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">
                    {getTierIcon(selectedClient.tier)}
                  </span>
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      {selectedClient.name}
                    </h3>
                    <p className="text-gray-400">
                      {selectedClient.environment}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedClient(null)}
                  className="text-gray-400 hover:text-white text-xl"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Client Info Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 bg-gray-700/30 rounded">
                  <div className="text-sm text-gray-400">Tier</div>
                  <div className="text-white font-semibold">
                    {selectedClient.tier}
                  </div>
                </div>
                <div className="p-3 bg-gray-700/30 rounded">
                  <div className="text-sm text-gray-400">Business Hours</div>
                  <div className="text-white font-semibold">
                    {selectedClient.business_hours}
                  </div>
                </div>
                <div className="p-3 bg-gray-700/30 rounded">
                  <div className="text-sm text-gray-400">Critical Systems</div>
                  <div className="text-white font-semibold">
                    {selectedClient.critical_systems.length}
                  </div>
                </div>
                <div className="p-3 bg-gray-700/30 rounded">
                  <div className="text-sm text-gray-400">Environment</div>
                  <div className="text-white font-semibold text-xs">
                    {selectedClient.environment}
                  </div>
                </div>
              </div>

              {/* Current Alerts */}
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">
                  Current Alerts
                </h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {alerts
                    .filter((alert) => alert.client_id === selectedClient.id)
                    .slice(0, 10)
                    .map((alert) => (
                      <div
                        key={alert.id}
                        className={`p-3 rounded border ${
                          alert.severity === "critical"
                            ? "border-red-500/30 bg-red-900/10"
                            : alert.severity === "warning"
                            ? "border-yellow-500/30 bg-yellow-900/10"
                            : "border-gray-600 bg-gray-700/20"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <span
                              className={`px-2 py-1 text-xs rounded ${
                                alert.severity === "critical"
                                  ? "bg-red-600 text-white"
                                  : alert.severity === "warning"
                                  ? "bg-yellow-600 text-white"
                                  : "bg-blue-600 text-white"
                              }`}
                            >
                              {alert.severity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">
                              {alert.system}
                            </span>
                          </div>
                          <span className="text-xs text-gray-400">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-gray-300 text-sm">{alert.message}</p>
                        {alert.cascade_risk > 0.5 && (
                          <div className="mt-1 text-xs text-yellow-400">
                            ⚡ {Math.round(alert.cascade_risk * 100)}% cascade
                            risk
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              </div>

              {/* System Dependencies */}
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">
                  System Dependencies
                </h4>
                <div className="grid gap-3">
                  {Object.entries(selectedClient.system_dependencies).map(
                    ([system, dependencies]) => (
                      <div key={system} className="p-3 bg-gray-700/20 rounded">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-white font-medium">
                            {system}
                          </span>
                          <span className="text-gray-400">→</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {dependencies.map((dep) => (
                            <span
                              key={dep}
                              className="px-2 py-1 bg-blue-600 text-white text-xs rounded"
                            >
                              {dep}
                            </span>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Active Predictions */}
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">
                  Active Cascade Predictions
                </h4>
                <div className="space-y-3">
                  {predictions
                    .filter((pred) => pred.client_id === selectedClient.id)
                    .map((prediction) => (
                      <div
                        key={prediction.alert_id}
                        className="p-3 bg-orange-900/10 border border-orange-500/20 rounded"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-white font-medium">
                            Cascade Prediction
                          </span>
                          <div className="flex space-x-2">
                            <span className="px-2 py-1 bg-orange-600 text-white text-xs rounded">
                              {Math.round(
                                prediction.prediction_confidence * 100
                              )}
                              % confidence
                            </span>
                            <span className="px-2 py-1 bg-red-600 text-white text-xs rounded">
                              {prediction.time_to_cascade_minutes}min
                            </span>
                          </div>
                        </div>
                        <div className="text-sm text-gray-300 mb-2">
                          Will affect:{" "}
                          {prediction.predicted_cascade_systems.join(", ")}
                        </div>
                        {prediction.prevention_actions &&
                          prediction.prevention_actions.length > 0 && (
                            <div className="text-sm text-blue-300">
                              Suggested action:{" "}
                              {prediction.prevention_actions[0]}
                            </div>
                          )}
                      </div>
                    ))}
                  {predictions.filter(
                    (pred) => pred.client_id === selectedClient.id
                  ).length === 0 && (
                    <div className="text-center py-6 text-gray-400">
                      <span className="text-2xl block mb-2">✅</span>
                      <p>No cascade predictions - all systems stable</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-600 flex justify-end space-x-3">
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors">
                View Full Report
              </button>
              <button
                onClick={() => setSelectedClient(null)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientOverview;
