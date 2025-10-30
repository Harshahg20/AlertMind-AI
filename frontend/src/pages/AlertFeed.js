import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  AlertCircle,
  Info,
  BarChart3,
  Shield,
  Wifi,
  HardDrive,
  Server,
  Filter,
  Users,
  Activity,
} from "lucide-react";
import { AlertFeedSkeleton } from "../components/SkeletonLoader";

const AlertFeed = ({ alerts, filteredData, loading }) => {
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [selectedClient, setSelectedClient] = useState("all");
  const [clientAlerts, setClientAlerts] = useState(alerts || []);

  useEffect(() => {
    setClientAlerts(alerts || []);
  }, [alerts]);

  if (loading) {
    return <AlertFeedSkeleton />;
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "critical":
        return "border-red-500 bg-red-900/10";
      case "warning":
        return "border-yellow-500 bg-yellow-900/10";
      case "info":
        return "border-blue-500 bg-blue-900/10";
      default:
        return "border-gray-500 bg-gray-900/10";
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "critical":
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case "warning":
        return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case "info":
        return <Info className="w-4 h-4 text-blue-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case "performance":
        return <BarChart3 className="w-4 h-4 text-yellow-400" />;
      case "security":
        return <Shield className="w-4 h-4 text-red-400" />;
      case "network":
        return <Wifi className="w-4 h-4 text-blue-400" />;
      case "storage":
        return <HardDrive className="w-4 h-4 text-green-400" />;
      case "system":
        return <Server className="w-4 h-4 text-purple-400" />;
      default:
        return <Activity className="w-4 h-4 text-gray-400" />;
    }
  };

  // Get unique clients for filter dropdown from both critical and noise alerts
  const allAlertsForClients = [
    ...(filteredData ? filteredData.critical_alerts || [] : []),
    ...(filteredData ? filteredData.noise_alerts || [] : []),
    ...(alerts || []),
  ];
  const uniqueClients = [
    ...new Set(allAlertsForClients.map((alert) => alert.client_name)),
  ];

  // Filter alerts based on selected filters
  const filteredAlerts = clientAlerts.filter((alert) => {
    if (selectedFilter !== "all" && alert.severity !== selectedFilter)
      return false;
    if (selectedClient !== "all" && alert.client_name !== selectedClient)
      return false;
    return true;
  });

  const handleClientChange = (clientName) => {
    setSelectedClient(clientName);
  };

  const handleFilterChange = (filterValue) => {
    setSelectedFilter(filterValue);
  };

  // Get the base alerts to work with
  const baseAlerts = filteredData ? filteredData.critical_alerts : clientAlerts;

  // Apply client and severity filters to the base alerts
  const criticalAlerts = baseAlerts.filter((alert) => {
    if (selectedFilter !== "all" && alert.severity !== selectedFilter)
      return false;
    if (selectedClient !== "all" && alert.client_name !== selectedClient)
      return false;
    return true;
  });

  // Apply filters to noise alerts as well
  const baseNoiseAlerts = filteredData ? filteredData.noise_alerts : [];
  const noiseAlerts = baseNoiseAlerts.filter((alert) => {
    if (selectedFilter !== "all" && alert.severity !== selectedFilter)
      return false;
    if (selectedClient !== "all" && alert.client_name !== selectedClient)
      return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header with filtering summary */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center">
              <AlertTriangle className="w-6 h-6 mr-2 text-red-400" />
              Intelligent Alert Feed
            </h2>
            <p className="text-gray-400 text-sm">
              AI-powered noise reduction and correlation engine
            </p>
          </div>

          {filteredData && (
            <div className="text-right">
              <div
                className={`text-2xl font-bold ${
                  filteredData.summary.noise_reduction_percent >= 0
                    ? "text-green-400"
                    : "text-red-400"
                }`}
              >
                {filteredData.summary.noise_reduction_percent >= 0 ? "-" : "+"}
                {Math.abs(filteredData.summary.noise_reduction_percent)}%
              </div>
              <div className="text-sm text-gray-400">
                {filteredData.summary.noise_reduction_percent >= 0
                  ? "Alert noise reduced"
                  : "Alert noise increased"}
              </div>
            </div>
          )}
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap gap-4 mb-4">
          {(selectedFilter !== "all" || selectedClient !== "all") && (
            <div className="flex items-center space-x-2 text-sm text-blue-400">
              <span>🔍 Filters Active:</span>
              {selectedFilter !== "all" && (
                <span className="px-2 py-1 bg-blue-600 text-white rounded text-xs">
                  Severity: {selectedFilter}
                </span>
              )}
              {selectedClient !== "all" && (
                <span className="px-2 py-1 bg-blue-600 text-white rounded text-xs">
                  Client: {selectedClient}
                </span>
              )}
              <button
                onClick={() => {
                  setSelectedFilter("all");
                  setSelectedClient("all");
                }}
                className="px-2 py-1 bg-gray-600 hover:bg-gray-500 text-white rounded text-xs transition-colors"
              >
                Clear All
              </button>
            </div>
          )}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <label className="text-sm text-gray-400">Severity:</label>
            <select
              value={selectedFilter}
              onChange={(e) => handleFilterChange(e.target.value)}
              className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 text-sm"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-gray-400" />
            <label className="text-sm text-gray-400">Client:</label>
            <select
              value={selectedClient}
              onChange={(e) => handleClientChange(e.target.value)}
              className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 text-sm"
            >
              <option value="all">All Clients</option>
              {uniqueClients.map((client) => (
                <option key={client} value={client}>
                  {client}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Quick Stats */}
        {filteredData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-700/30 rounded">
              <div className="text-lg font-bold text-white">
                {filteredData.summary.total_alerts}
              </div>
              <div className="text-xs text-gray-400">Original</div>
            </div>
            <div className="text-center p-3 bg-green-900/20 rounded border border-green-500/20">
              <div className="text-lg font-bold text-green-400">
                {criticalAlerts.length}
              </div>
              <div className="text-xs text-gray-400">Filtered Critical</div>
            </div>
            <div className="text-center p-3 bg-blue-900/20 rounded border border-blue-500/20">
              <div className="text-lg font-bold text-blue-400">
                {filteredData.summary.correlated_groups}
              </div>
              <div className="text-xs text-gray-400">Correlated Groups</div>
            </div>
            <div className="text-center p-3 bg-yellow-900/20 rounded border border-yellow-500/20">
              <div className="text-lg font-bold text-yellow-400">
                {noiseAlerts.length}
              </div>
              <div className="text-xs text-gray-400">Filtered Noise</div>
            </div>
          </div>
        )}
      </div>

      {/* Critical Alerts Section */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700 bg-green-900/10">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <span className="mr-2">✅</span>
            Critical Alerts ({criticalAlerts.length})
            <span className="ml-2 px-2 py-1 bg-green-600 text-white text-xs rounded-full">
              AI Filtered
            </span>
          </h3>
          <p className="text-sm text-gray-400">
            High-priority alerts requiring attention
          </p>
        </div>

        <div className="p-4 max-h-96 overflow-y-auto">
          {criticalAlerts.length > 0 ? (
            <div className="space-y-3">
              {criticalAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-4 rounded-lg border ${getSeverityColor(
                    alert.severity
                  )} transition-all hover:bg-gray-700/20`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">
                        {getSeverityIcon(alert.severity)}
                      </span>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold text-white">
                            {alert.client_name}
                          </span>
                          <span className="text-sm text-gray-400">•</span>
                          <span className="text-sm text-gray-300">
                            {alert.system}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 mt-1">
                          <span
                            className={`px-2 py-1 text-xs rounded-full ${
                              alert.severity === "critical"
                                ? "bg-red-600 text-white"
                                : alert.severity === "warning"
                                ? "bg-yellow-600 text-white"
                                : "bg-blue-600 text-white"
                            }`}
                          >
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-400 flex items-center">
                            {getCategoryIcon(alert.category)} {alert.category}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                      {alert.cascade_risk > 0.5 && (
                        <div className="mt-1 flex items-center justify-end">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                          <span className="text-xs text-yellow-400">
                            {Math.round(alert.cascade_risk * 100)}% cascade risk
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <p className="text-gray-200 mb-2">{alert.message}</p>

                  {alert.is_correlated && (
                    <div className="mt-2 p-2 bg-blue-900/20 border border-blue-500/20 rounded">
                      <span className="text-xs text-blue-400 font-medium">
                        🔗 Correlated with{" "}
                        {alert.correlated_with
                          ? alert.correlated_with.length
                          : 0}{" "}
                        other alerts
                      </span>
                    </div>
                  )}

                  {alert.affected_systems &&
                    alert.affected_systems.length > 0 && (
                      <div className="mt-2 text-sm text-gray-400">
                        <span className="font-medium">May affect:</span>{" "}
                        {alert.affected_systems.join(", ")}
                      </div>
                    )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <span className="text-4xl mb-2 block">🎉</span>
              <p>No critical alerts! All systems operating normally.</p>
            </div>
          )}
        </div>
      </div>

      {/* Filtered Noise Section */}
      {noiseAlerts.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700 bg-gray-900/50">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <span className="mr-2">🔇</span>
              Filtered Noise ({noiseAlerts.length})
              <span className="ml-2 px-2 py-1 bg-gray-600 text-white text-xs rounded-full">
                AI Filtered
              </span>
            </h3>
            <p className="text-sm text-gray-400">
              Low-priority alerts automatically filtered
            </p>
          </div>

          <div className="p-4 max-h-64 overflow-y-auto">
            <div className="space-y-2">
              {noiseAlerts.slice(0, 10).map((alert) => (
                <div
                  key={alert.id}
                  className="p-3 rounded bg-gray-700/20 border border-gray-600/30 text-sm"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400">
                        {getSeverityIcon("info")}
                      </span>
                      <span className="text-gray-300">{alert.client_name}</span>
                      <span className="text-gray-500">•</span>
                      <span className="text-gray-400">{alert.system}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-gray-400 mt-1 text-xs">{alert.message}</p>
                </div>
              ))}
            </div>
            {noiseAlerts.length > 10 && (
              <div className="mt-3 text-center">
                <span className="text-sm text-gray-500">
                  ... and {noiseAlerts.length - 10} more filtered alerts
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertFeed;
