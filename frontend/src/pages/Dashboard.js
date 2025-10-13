import React from "react";

const Dashboard = ({ stats, alerts, predictions, filteredData, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const highRiskPredictions = predictions.filter(
    (p) => p.prediction_confidence > 0.7 && p.time_to_cascade_minutes < 20
  );

  const criticalAlerts = alerts.filter((a) => a.severity === "critical");

  return (
    <div className="space-y-6">
      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Alerts */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Alerts</p>
              <p className="text-2xl font-bold text-white">
                {stats.total_alerts || 0}
              </p>
            </div>
            <div className="bg-blue-600 p-3 rounded-full">
              <span className="text-xl">📊</span>
            </div>
          </div>
          {filteredData && (
            <div className="mt-2">
              <p className="text-green-400 text-sm">
                ↓ {filteredData.summary.noise_reduction_percent}% noise filtered
              </p>
            </div>
          )}
        </div>

        {/* Critical Alerts */}
        <div className="bg-gray-800 rounded-lg p-6 border border-red-500/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Critical Alerts</p>
              <p className="text-2xl font-bold text-red-400">
                {stats.critical_alerts || 0}
              </p>
            </div>
            <div className="bg-red-600 p-3 rounded-full">
              <span className="text-xl">🚨</span>
            </div>
          </div>
          <div className="mt-2">
            <p className="text-gray-400 text-sm">
              {stats.critical_percentage || 0}% of total alerts
            </p>
          </div>
        </div>

        {/* Cascade Predictions */}
        <div className="bg-gray-800 rounded-lg p-6 border border-yellow-500/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Predictions</p>
              <p className="text-2xl font-bold text-yellow-400">
                {predictions.length}
              </p>
            </div>
            <div className="bg-yellow-600 p-3 rounded-full">
              <span className="text-xl">⚡</span>
            </div>
          </div>
          <div className="mt-2">
            <p className="text-yellow-400 text-sm">
              {highRiskPredictions.length} high-risk cascades
            </p>
          </div>
        </div>

        {/* Efficiency Gain */}
        <div className="bg-gray-800 rounded-lg p-6 border border-green-500/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Efficiency Gain</p>
              <p className="text-2xl font-bold text-green-400">
                {filteredData
                  ? filteredData.summary.noise_reduction_percent
                  : 0}
                %
              </p>
            </div>
            <div className="bg-green-600 p-3 rounded-full">
              <span className="text-xl">📈</span>
            </div>
          </div>
          <div className="mt-2">
            <p className="text-green-400 text-sm">Alert noise reduction</p>
          </div>
        </div>
      </div>

      {/* High-Risk Cascade Alerts */}
      {highRiskPredictions.length > 0 && (
        <div className="bg-gradient-to-r from-red-900/20 to-orange-900/20 border border-red-500/30 rounded-lg p-6">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-2xl">🚨</span>
            <h2 className="text-xl font-bold text-red-400">
              URGENT: High-Risk Cascade Predictions
            </h2>
          </div>
          <div className="grid gap-4">
            {highRiskPredictions.slice(0, 3).map((prediction) => {
              const alert = alerts.find((a) => a.id === prediction.alert_id);
              return (
                <div
                  key={prediction.alert_id}
                  className="bg-gray-800/50 rounded-lg p-4 border border-red-500/30"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <span className="font-semibold text-white">
                        {alert
                          ? `${alert.client_name} - ${alert.system}`
                          : "Unknown Alert"}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 bg-red-600 text-white text-xs rounded-full">
                        {Math.round(prediction.prediction_confidence * 100)}%
                        confidence
                      </span>
                      <span className="px-2 py-1 bg-orange-600 text-white text-xs rounded-full">
                        {prediction.time_to_cascade_minutes}min to cascade
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm mb-2">
                    {alert ? alert.message : "Alert details unavailable"}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-400">
                      Will affect:{" "}
                      {prediction.predicted_cascade_systems.join(", ")}
                    </div>
                    <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                      Take Action
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alert Intelligence Summary */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <span className="mr-2">🧠</span>
            Alert Intelligence Summary
          </h3>

          {filteredData && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded">
                <span className="text-gray-300">Original Alerts</span>
                <span className="text-white font-semibold">
                  {filteredData.summary.total_alerts}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-green-900/20 rounded border border-green-500/20">
                <span className="text-gray-300">After AI Filtering</span>
                <span className="text-green-400 font-semibold">
                  {filteredData.summary.critical_alerts}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-blue-900/20 rounded border border-blue-500/20">
                <span className="text-gray-300">Correlated Groups</span>
                <span className="text-blue-400 font-semibold">
                  {filteredData.summary.correlated_groups}
                </span>
              </div>

              <div className="pt-3 border-t border-gray-600">
                <p className="text-sm text-gray-400 mb-2">Processing Impact:</p>
                <p className="text-green-400 text-sm font-medium">
                  {filteredData.summary.efficiency_improvement}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Processing time: {filteredData.total_processing_time_ms}ms
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Recent Critical Alerts */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <span className="mr-2">⚠️</span>
            Recent Critical Alerts
          </h3>

          <div className="space-y-3 max-h-80 overflow-y-auto">
            {criticalAlerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className="p-3 bg-red-900/10 border border-red-500/20 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-red-400">
                    {alert.client_name}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-white mb-1">{alert.system}</p>
                <p className="text-xs text-gray-300">{alert.message}</p>
                {alert.cascade_risk > 0.7 && (
                  <div className="mt-2 flex items-center">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                    <span className="text-xs text-yellow-400">
                      High cascade risk ({Math.round(alert.cascade_risk * 100)}
                      %)
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Client Performance Overview */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <span className="mr-2">👥</span>
            Client Alert Distribution
          </h3>

          {stats.client_breakdown && (
            <div className="space-y-3">
              {Object.entries(stats.client_breakdown).map(
                ([clientName, clientStats]) => (
                  <div
                    key={clientName}
                    className="p-3 bg-gray-700/30 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">
                        {clientName}
                      </span>
                      <span className="text-sm text-gray-400">
                        {clientStats.total_alerts} alerts
                      </span>
                    </div>
                    <div className="flex space-x-4 text-sm">
                      <span className="text-red-400">
                        {clientStats.critical_alerts} critical
                      </span>
                      <span className="text-yellow-400">
                        {clientStats.high_cascade_risk} high-risk
                      </span>
                    </div>
                    {/* Simple visual bar */}
                    <div className="mt-2 w-full bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-red-500 to-yellow-500 h-2 rounded-full"
                        style={{
                          width: `${
                            (clientStats.critical_alerts /
                              clientStats.total_alerts) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </div>

        {/* System Categories Breakdown */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <span className="mr-2">📋</span>
            Alert Categories
          </h3>

          {stats.category_breakdown && (
            <div className="space-y-3">
              {Object.entries(stats.category_breakdown)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 6)
                .map(([category, count]) => (
                  <div
                    key={category}
                    className="flex items-center justify-between p-2 bg-gray-700/20 rounded"
                  >
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          category === "performance"
                            ? "bg-yellow-500"
                            : category === "security"
                            ? "bg-red-500"
                            : category === "network"
                            ? "bg-blue-500"
                            : category === "storage"
                            ? "bg-green-500"
                            : category === "system"
                            ? "bg-purple-500"
                            : "bg-gray-500"
                        }`}
                      ></div>
                      <span className="text-gray-300 capitalize">
                        {category}
                      </span>
                    </div>
                    <span className="text-white font-semibold">{count}</span>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Cross-Client Intelligence Teaser */}
      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white flex items-center">
              <span className="mr-2">🔗</span>
              Cross-Client Intelligence Active
            </h3>
            <p className="text-gray-300 text-sm">
              Learning from patterns across all{" "}
              {Object.keys(stats.client_breakdown || {}).length} clients
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-blue-400">
              {predictions.length}
            </p>
            <p className="text-sm text-gray-400">Active predictions</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="p-3 bg-blue-900/20 rounded border border-blue-500/20">
            <p className="text-lg font-bold text-blue-400">
              {Math.round(
                (predictions.reduce(
                  (acc, p) => acc + p.prediction_confidence,
                  0
                ) /
                  predictions.length) *
                  100
              ) || 0}
              %
            </p>
            <p className="text-xs text-gray-400">Avg Confidence</p>
          </div>
          <div className="p-3 bg-green-900/20 rounded border border-green-500/20">
            <p className="text-lg font-bold text-green-400">
              {predictions.filter((p) => p.time_to_cascade_minutes < 15).length}
            </p>
            <p className="text-xs text-gray-400">Urgent (&15min)</p>
          </div>
          <div className="p-3 bg-purple-900/20 rounded border border-purple-500/20">
            <p className="text-lg font-bold text-purple-400">
              {predictions.reduce(
                (acc, p) => acc + p.predicted_cascade_systems.length,
                0
              )}
            </p>
            <p className="text-xs text-gray-400">Systems at Risk</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
