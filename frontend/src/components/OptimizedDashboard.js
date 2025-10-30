import React, { useState, useEffect } from "react";
import {
  BarChart3,
  Brain,
  Monitor,
  AlertTriangle,
  Activity,
  Users,
  Zap,
  TrendingUp,
  Shield,
  Clock,
  XCircle,
  AlertCircle,
  Info,
} from "lucide-react";
import EnhancedAIInsights from "./EnhancedAIInsights";
import SystemHealthDashboard from "./SystemHealthDashboard";
import { DashboardSkeleton } from "./SkeletonLoader";

const OptimizedDashboard = ({
  stats,
  alerts,
  predictions,
  filteredData,
  loading,
}) => {
  const [activeView, setActiveView] = useState("overview");
  const [clientStats, setClientStats] = useState({});
  const [selectedClient, setSelectedClient] = useState("all");

  useEffect(() => {
    if (alerts.length > 0) {
      calculateClientStats();
    }
  }, [alerts, predictions]);

  const calculateClientStats = () => {
    const stats = {};
    alerts.forEach((alert) => {
      if (!stats[alert.client_id]) {
        stats[alert.client_id] = {
          name: alert.client_name,
          totalAlerts: 0,
          criticalAlerts: 0,
          warningAlerts: 0,
          predictions: 0,
          highRiskPredictions: 0,
          avgCascadeRisk: 0,
        };
      }

      stats[alert.client_id].totalAlerts++;
      if (alert.severity === "critical")
        stats[alert.client_id].criticalAlerts++;
      if (alert.severity === "warning") stats[alert.client_id].warningAlerts++;
    });

    predictions.forEach((pred) => {
      if (stats[pred.client_id]) {
        stats[pred.client_id].predictions++;
        if (pred.prediction_confidence > 0.7) {
          stats[pred.client_id].highRiskPredictions++;
        }
      }
    });

    // Calculate average cascade risk
    Object.keys(stats).forEach((clientId) => {
      const clientAlerts = alerts.filter((a) => a.client_id === clientId);
      if (clientAlerts.length > 0) {
        stats[clientId].avgCascadeRisk =
          clientAlerts.reduce((acc, a) => acc + (a.cascade_risk || 0), 0) /
          clientAlerts.length;
      }
    });

    setClientStats(stats);
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  const highRiskPredictions = predictions.filter(
    (p) => p.prediction_confidence > 0.7 && p.time_to_cascade_minutes < 20
  );

  const criticalAlerts = alerts.filter((a) => a.severity === "critical");

  const getTierColor = (tier) => {
    switch (tier?.toLowerCase()) {
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

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "critical":
        return <XCircle className="w-4 h-4 text-red-400" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case "info":
        return <Info className="w-4 h-4 text-blue-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Enhanced Navigation */}
      <div className="flex space-x-1 bg-gray-800/50 rounded-lg p-1">
        {[
          { id: "overview", label: "Overview", icon: BarChart3 },
          { id: "ai-insights", label: "AI Insights", icon: Brain },
          { id: "system-health", label: "System Health", icon: Monitor },
          { id: "clients", label: "Clients", icon: Users },
        ].map((view) => (
          <button
            key={view.id}
            onClick={() => setActiveView(view.id)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
              activeView === view.id
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-700/50"
            }`}
          >
            <view.icon className="w-4 h-4" />
            <span>{view.label}</span>
          </button>
        ))}
      </div>

      {/* Render Active View */}
      {activeView === "ai-insights" && <EnhancedAIInsights />}
      {activeView === "system-health" && <SystemHealthDashboard />}

      {activeView === "clients" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center">
                <Users className="w-6 h-6 mr-2" />
                Client Overview
              </h2>
              <p className="text-gray-400 text-sm">
                Monitor and manage all client systems
              </p>
            </div>
            <select
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
            >
              <option value="all">All Clients</option>
              {Object.keys(clientStats).map((clientId) => (
                <option key={clientId} value={clientId}>
                  {clientStats[clientId].name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(clientStats)
              .filter(
                ([clientId]) =>
                  selectedClient === "all" || clientId === selectedClient
              )
              .map(([clientId, clientData]) => (
                <div
                  key={clientId}
                  className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">
                      {clientData.name}
                    </h3>
                    <div
                      className={`px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getTierColor(
                        "premium"
                      )} text-white`}
                    >
                      Premium
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Total Alerts:</span>
                      <span className="text-white">
                        {clientData.totalAlerts}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Critical:</span>
                      <span className="text-red-400">
                        {clientData.criticalAlerts}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Predictions:</span>
                      <span className="text-blue-400">
                        {clientData.predictions}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">High Risk:</span>
                      <span className="text-orange-400">
                        {clientData.highRiskPredictions}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Avg Risk:</span>
                      <span className="text-white">
                        {(clientData.avgCascadeRisk * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {activeView === "overview" && (
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
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
              </div>
              {filteredData && (
                <div className="mt-2">
                  <p
                    className={`text-sm flex items-center ${
                      filteredData.summary.noise_reduction_percent >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {filteredData.summary.noise_reduction_percent >= 0
                      ? "↓"
                      : "↑"}{" "}
                    {Math.abs(filteredData.summary.noise_reduction_percent)}%
                    noise
                    {filteredData.summary.noise_reduction_percent >= 0
                      ? " filtered"
                      : " increased"}
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
                  <AlertTriangle className="w-6 h-6 text-white" />
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
                  <Zap className="w-6 h-6 text-white" />
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
                  <Shield className="w-6 h-6 text-white" />
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
                <AlertTriangle className="w-6 h-6 text-red-400" />
                <h2 className="text-xl font-bold text-red-400">
                  URGENT: High-Risk Cascade Predictions
                </h2>
              </div>
              <div className="grid gap-4">
                {highRiskPredictions.slice(0, 3).map((prediction) => {
                  const alert = alerts.find(
                    (a) => a.id === prediction.alert_id
                  );
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
                          <span className="px-2 py-1 bg-red-600 text-white text-xs rounded-full flex items-center">
                            <Activity className="w-3 h-3 mr-1" />
                            {Math.round(prediction.prediction_confidence * 100)}
                            % confidence
                          </span>
                          <span className="px-2 py-1 bg-orange-600 text-white text-xs rounded-full flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
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
                        <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors flex items-center">
                          <Shield className="w-3 h-3 mr-1" />
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
                <Brain className="w-5 h-5 mr-2" />
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
                    <p className="text-sm text-gray-400 mb-2">
                      Processing Impact:
                    </p>
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
                <AlertTriangle className="w-5 h-5 mr-2" />
                Recent Critical Alerts
              </h3>

              <div className="space-y-3 max-h-80 overflow-y-auto">
                {criticalAlerts.slice(0, 5).map((alert) => (
                  <div
                    key={alert.id}
                    className="p-3 bg-red-900/10 border border-red-500/20 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-red-400 flex items-center">
                        {getSeverityIcon(alert.severity)}
                        <span className="ml-2">{alert.client_name}</span>
                      </span>
                      <span className="text-xs text-gray-400 flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-white mb-1">{alert.system}</p>
                    <p className="text-xs text-gray-300">{alert.message}</p>
                    {alert.cascade_risk > 0.7 && (
                      <div className="mt-2 flex items-center">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                        <span className="text-xs text-yellow-400">
                          High cascade risk (
                          {Math.round(alert.cascade_risk * 100)}
                          %)
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cross-Client Intelligence */}
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Cross-Client Intelligence Active
                </h3>
                <p className="text-gray-300 text-sm">
                  Learning from patterns across all{" "}
                  {Object.keys(clientStats).length} clients
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
                  {
                    predictions.filter((p) => p.time_to_cascade_minutes < 15)
                      .length
                  }
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
      )}
    </div>
  );
};

export default OptimizedDashboard;
