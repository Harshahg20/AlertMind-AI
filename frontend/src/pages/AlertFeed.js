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
  Zap,
  GitBranch,
  CheckCircle2,
  ArrowRight,
  Layout,
  List,
} from "lucide-react";
import { AlertFeedSkeleton } from "../components/SkeletonLoader";

const AlertFeed = ({ alerts, filteredData, loading, onNavigate }) => {
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [selectedClient, setSelectedClient] = useState("all");
  const [clientAlerts, setClientAlerts] = useState(alerts || []);
  const [viewMode, setViewMode] = useState("grouped"); // 'grouped' or 'list'

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

  // Mock Incident Grouping Logic
  const getIncidents = () => {
    // In a real app, this would come from the backend AI analysis
    const incidents = [];
    
    if (criticalAlerts.length > 0) {
      // Create a "Patch Caused" incident if we have critical alerts
      incidents.push({
        id: "inc-001",
        title: "Cascading Service Failure Detected",
        severity: "critical",
        client: "TechCorp",
        root_cause: "Recent Patch Deployment (KB-45992) caused Memory Leak",
        confidence: 98,
        affected_systems: ["Web-01", "DB-Shard-04", "Auth-Service"],
        alerts_count: criticalAlerts.length,
        timestamp: new Date().toISOString(),
        status: "active",
        recommendation: "Rollback Patch KB-45992 immediately",
        action_link: "patch"
      });
    }
    
    // Add a secondary incident if we have enough data
    if (criticalAlerts.length > 3) {
       incidents.push({
        id: "inc-002",
        title: "Unusual Network Traffic Pattern",
        severity: "warning",
        client: "FinServe",
        root_cause: "Potential DDoS Attack Signature",
        confidence: 85,
        affected_systems: ["Gateway-01", "Firewall-Main"],
        alerts_count: 2,
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        status: "investigating",
        recommendation: "Enable Traffic Shaping Rule #44",
        action_link: "security"
      });
    }

    return incidents;
  };

  const incidents = getIncidents();

  return (
    <div className="space-y-6">
      {/* Header with filtering summary */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center">
              <Zap className="w-6 h-6 mr-2 text-yellow-400" />
              Intelligent Alert Feed
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              AI-powered noise reduction and correlation engine
            </p>
          </div>

          <div className="flex items-center bg-gray-700/50 p-1 rounded-lg border border-gray-600">
            <button
              onClick={() => setViewMode("grouped")}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all ${
                viewMode === "grouped"
                  ? "bg-blue-600 text-white shadow-lg"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <GitBranch className="w-4 h-4 mr-2" />
              AI Incident View
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all ${
                viewMode === "list"
                  ? "bg-blue-600 text-white shadow-lg"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <List className="w-4 h-4 mr-2" />
              Raw Alert List
            </button>
          </div>
        </div>

        {/* Stats Row */}
        {filteredData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-2">
             <div className="text-center p-3 bg-gray-700/30 rounded border border-gray-600/30">
              <div className="text-2xl font-bold text-white">
                {filteredData.summary.total_alerts}
              </div>
              <div className="text-xs text-gray-400 uppercase tracking-wider">Total Signals</div>
            </div>
            <div className="text-center p-3 bg-blue-900/20 rounded border border-blue-500/20">
              <div className="text-2xl font-bold text-blue-400">
                {incidents.length}
              </div>
              <div className="text-xs text-gray-400 uppercase tracking-wider">Active Incidents</div>
            </div>
             <div className="text-center p-3 bg-green-900/20 rounded border border-green-500/20">
              <div className="text-2xl font-bold text-green-400">
                {Math.abs(filteredData.summary.noise_reduction_percent)}%
              </div>
              <div className="text-xs text-gray-400 uppercase tracking-wider">Noise Reduced</div>
            </div>
            <div className="text-center p-3 bg-purple-900/20 rounded border border-purple-500/20">
              <div className="text-2xl font-bold text-purple-400">
                98%
              </div>
              <div className="text-xs text-gray-400 uppercase tracking-wider">AI Confidence</div>
            </div>
          </div>
        )}
      </div>

      {viewMode === "grouped" ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Active Incidents (AI Correlated)</h3>
            <span className="text-xs text-gray-400">Sorted by Priority</span>
          </div>
          
          {incidents.map((incident) => (
            <div key={incident.id} className="bg-gray-800 rounded-lg border border-l-4 border-gray-700 border-l-red-500 overflow-hidden hover:border-gray-600 transition-all shadow-lg">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                       <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs font-bold rounded uppercase border border-red-500/30">
                        {incident.severity}
                      </span>
                      <h3 className="text-xl font-bold text-white">{incident.title}</h3>
                    </div>
                    
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-3">
                        <div className="flex items-start">
                          <div className="mt-1 mr-3 bg-blue-500/20 p-1.5 rounded">
                            <Activity className="w-4 h-4 text-blue-400" />
                          </div>
                          <div>
                            <div className="text-sm text-gray-400">Root Cause Analysis</div>
                            <div className="text-base text-white font-medium">{incident.root_cause}</div>
                            <div className="text-xs text-green-400 mt-1 flex items-center">
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              {incident.confidence}% AI Confidence
                            </div>
                          </div>
                        </div>

                        <div className="flex items-start">
                          <div className="mt-1 mr-3 bg-purple-500/20 p-1.5 rounded">
                            <Server className="w-4 h-4 text-purple-400" />
                          </div>
                          <div>
                            <div className="text-sm text-gray-400">Affected Scope</div>
                            <div className="text-sm text-gray-300">
                              Client: <span className="text-white font-medium">{incident.client}</span>
                            </div>
                            <div className="text-sm text-gray-300">
                              Systems: {incident.affected_systems.join(", ")}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                        <div className="text-sm text-gray-400 mb-2">AI Recommendation</div>
                        <div className="text-white font-medium mb-3">
                          {incident.recommendation}
                        </div>
                        <button 
                          onClick={() => onNavigate && onNavigate(incident.action_link, {
                            client: incident.client,
                            target: incident.affected_systems[0],
                            action: "Rollback Patch KB-45992",
                            root_cause: incident.root_cause
                          })}
                          className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded flex items-center justify-center transition-colors text-sm font-medium"
                        >
                          Execute Remediation
                          <ArrowRight className="w-4 h-4 ml-2" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 pt-4 border-t border-gray-700 flex items-center justify-between text-sm text-gray-400">
                  <div>
                    Aggregated <span className="text-white font-medium">{incident.alerts_count} alerts</span> into this incident
                  </div>
                  <div>
                    Last updated: {new Date(incident.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {incidents.length === 0 && (
             <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
              <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">All Systems Operational</h3>
              <p className="text-gray-400">No active incidents detected by AI correlation engine.</p>
            </div>
          )}
        </div>
      ) : (
        /* Original List View */
        <>
        {/* Filter Controls (Only show in List View) */}
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
      </>
      )}
    </div>
  );
};

export default AlertFeed;
