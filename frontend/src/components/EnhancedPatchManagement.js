import React, { useState, useEffect } from "react";
import {
  Shield,
  AlertTriangle,
  RefreshCw,
  BarChart3,
  Calendar,
  Zap,
  Target,
  Brain,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";
import { EnhancedPatchSkeleton } from "./SkeletonLoader";

const EnhancedPatchManagement = ({ clients = [], loading = false }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  const [cveDatabase, setCveDatabase] = useState([]);
  const [patchPlans, setPatchPlans] = useState({});
  const [cveAnalyses, setCveAnalyses] = useState({});
  const [maintenanceWindows, setMaintenanceWindows] = useState({});
  const [executionMonitoring, setExecutionMonitoring] = useState({});
  const [loadingData, setLoadingData] = useState(false);
  const [activeTab, setActiveTab] = useState("cve-analysis");
  const [selectedCves, setSelectedCves] = useState([]);

  useEffect(() => {
    if (clients.length > 0) {
      fetchCveDatabase();
    }
  }, [clients]);

  const fetchCveDatabase = async () => {
    try {
      setLoadingData(true);
      const response = await apiClient.get("/api/enhanced-patch/cve-database");
      setCveDatabase(response.data.cve_database || []);
    } catch (error) {
      console.error("Error fetching CVE database:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const analyzeCveForClient = async (clientId, cveId) => {
    try {
      setLoadingData(true);
      const response = await apiClient.get(
        `/api/enhanced-patch/cve-analysis/${clientId}?cve_id=${cveId}`
      );
      setCveAnalyses((prev) => ({
        ...prev,
        [`${clientId}_${cveId}`]: response.data.cve_analysis,
      }));
    } catch (error) {
      console.error("Error analyzing CVE:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const generatePatchPlan = async (clientId, cveList) => {
    try {
      setLoadingData(true);
      const response = await apiClient.post(
        `/api/enhanced-patch/patch-plan/${clientId}`,
        cveList
      );
      setPatchPlans((prev) => ({
        ...prev,
        [clientId]: response.data.patch_plan,
      }));
    } catch (error) {
      console.error("Error generating patch plan:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const optimizeMaintenanceWindows = async (clientId, patchPlan) => {
    try {
      setLoadingData(true);
      const response = await apiClient.post(
        `/api/enhanced-patch/optimize-maintenance/${clientId}`,
        patchPlan
      );
      setMaintenanceWindows((prev) => ({
        ...prev,
        [clientId]: response.data.optimization,
      }));
    } catch (error) {
      console.error("Error optimizing maintenance windows:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const monitorPatchExecution = async (clientId, windowId) => {
    try {
      const response = await apiClient.post(
        `/api/enhanced-patch/monitor-execution/${clientId}`,
        { window_id: windowId }
      );
      setExecutionMonitoring((prev) => ({
        ...prev,
        [`${clientId}_${windowId}`]: response.data.monitoring_data,
      }));
    } catch (error) {
      console.error("Error monitoring patch execution:", error);
    }
  };

  const handleCveSelection = (cveId, selected) => {
    if (selected) {
      setSelectedCves((prev) => [...prev, cveId]);
    } else {
      setSelectedCves((prev) => prev.filter((id) => id !== cveId));
    }
  };

  const handleGeneratePatchPlan = async () => {
    const clientId = selectedClient === "all" ? clients[0]?.id : selectedClient;
    if (!clientId || selectedCves.length === 0) return;

    const selectedCveData = cveDatabase.filter((cve) =>
      selectedCves.includes(cve.cve)
    );
    await generatePatchPlan(clientId, selectedCveData);
    setActiveTab("patch-plan");
  };

  const getSeverityColor = (severity) => {
    if (severity >= 9.0) return "text-red-400 bg-red-900/20";
    if (severity >= 7.0) return "text-orange-400 bg-orange-900/20";
    if (severity >= 5.0) return "text-yellow-400 bg-yellow-900/20";
    return "text-green-400 bg-green-900/20";
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "IMMEDIATE":
        return "text-red-400 bg-red-900/20";
      case "HIGH":
        return "text-orange-400 bg-orange-900/20";
      case "MEDIUM":
        return "text-yellow-400 bg-yellow-900/20";
      case "LOW":
        return "text-green-400 bg-green-900/20";
      default:
        return "text-gray-400 bg-gray-900/20";
    }
  };

  if (loading || loadingData) {
    return <EnhancedPatchSkeleton />;
  }

  const filteredClients =
    selectedClient === "all"
      ? clients
      : clients.filter((c) => c.id === selectedClient);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Shield className="w-6 h-6 mr-3 text-blue-400" />
            Enhanced Patch Management
          </h2>
          <p className="text-gray-400 mt-1">
            AI-powered CVE analysis, patch planning, and maintenance
            optimization
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">AI Active</span>
          </div>
          <button
            onClick={fetchCveDatabase}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Client Selector and Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <select
            value={selectedClient}
            onChange={(e) => setSelectedClient(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
          >
            <option value="all">All Clients</option>
            {clients.map((client) => (
              <option key={client.id} value={client.id}>
                {client.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
          {[
            { id: "cve-analysis", label: "CVE Analysis", icon: Brain },
            { id: "patch-plan", label: "Patch Plan", icon: Target },
            { id: "maintenance", label: "Maintenance", icon: Calendar },
            { id: "monitoring", label: "Monitoring", icon: BarChart3 },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-700"
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* CVE Analysis Tab */}
      {activeTab === "cve-analysis" && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-red-400" />
                CVE Database Analysis
              </h3>
              <div className="text-sm text-gray-400">
                {cveDatabase.length} CVEs available
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cveDatabase.map((cve) => (
                <div
                  key={cve.cve}
                  className="bg-gray-700/50 border border-gray-600 rounded-lg p-4 hover:bg-gray-700/70 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedCves.includes(cve.cve)}
                        onChange={(e) =>
                          handleCveSelection(cve.cve, e.target.checked)
                        }
                        className="rounded border-gray-600 bg-gray-800 text-blue-600"
                      />
                      <span className="font-mono text-sm text-blue-400">
                        {cve.cve}
                      </span>
                    </div>
                    <div
                      className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(
                        cve.severity
                      )}`}
                    >
                      {cve.severity}/10
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm text-gray-300">
                      <span className="text-gray-500">Product:</span>{" "}
                      {cve.product}
                    </div>
                    <div className="text-sm text-gray-300">
                      <span className="text-gray-500">Summary:</span>{" "}
                      {cve.summary}
                    </div>
                    <div className="text-xs text-gray-400">
                      Published: {cve.published_date}
                    </div>
                  </div>

                  <div className="mt-3 flex space-x-2">
                    <button
                      onClick={() =>
                        analyzeCveForClient(
                          selectedClient === "all"
                            ? clients[0]?.id
                            : selectedClient,
                          cve.cve
                        )
                      }
                      className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                    >
                      Analyze
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {selectedCves.length > 0 && (
              <div className="mt-6 flex justify-center">
                <button
                  onClick={handleGeneratePatchPlan}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  <Target className="w-5 h-5 mr-2" />
                  Generate Patch Plan ({selectedCves.length} CVEs)
                </button>
              </div>
            )}
          </div>

          {/* CVE Analysis Results */}
          {Object.keys(cveAnalyses).length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                AI Analysis Results
              </h3>
              <div className="space-y-4">
                {Object.entries(cveAnalyses).map(([key, analysis]) => (
                  <div
                    key={key}
                    className="bg-gray-700/50 border border-gray-600 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-mono text-blue-400">
                        {analysis.cve_id}
                      </span>
                      <div
                        className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                          analysis.patch_priority
                        )}`}
                      >
                        {analysis.patch_priority}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">
                          AI Analysis
                        </h4>
                        <div className="space-y-1 text-sm text-gray-400">
                          <div>
                            Impact Score:{" "}
                            {(analysis.client_impact * 100).toFixed(1)}%
                          </div>
                          <div>
                            Business Impact:{" "}
                            {analysis.ai_analysis?.business_impact || "N/A"}
                          </div>
                          <div>
                            Exploitability:{" "}
                            {analysis.ai_analysis?.exploitability || "N/A"}
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">
                          Recommendations
                        </h4>
                        <div className="space-y-1">
                          {analysis.ai_analysis?.recommended_actions
                            ?.slice(0, 3)
                            .map((action, idx) => (
                              <div key={idx} className="text-sm text-gray-400">
                                • {action}
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Patch Plan Tab */}
      {activeTab === "patch-plan" && (
        <div className="space-y-6">
          {Object.entries(patchPlans).map(([clientId, plan]) => (
            <div
              key={clientId}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Patch Plan for {plan.client_name}
                </h3>
                <div className="text-sm text-gray-400">
                  {plan.total_cves} CVEs • {plan.status}
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-md font-medium text-gray-300 mb-3">
                    CVE Analysis Summary
                  </h4>
                  <div className="space-y-3">
                    {plan.cve_analyses.map((analysis, idx) => (
                      <div
                        key={idx}
                        className="bg-gray-700/50 border border-gray-600 rounded-lg p-3"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono text-sm text-blue-400">
                            {analysis.cve_id}
                          </span>
                          <div
                            className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                              analysis.patch_priority
                            )}`}
                          >
                            {analysis.patch_priority}
                          </div>
                        </div>
                        <div className="text-sm text-gray-400">
                          {analysis.product} • Impact:{" "}
                          {(analysis.client_impact * 100).toFixed(1)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-md font-medium text-gray-300 mb-3">
                    Maintenance Windows
                  </h4>
                  <div className="space-y-3">
                    {plan.maintenance_windows.map((window, idx) => (
                      <div
                        key={idx}
                        className="bg-gray-700/50 border border-gray-600 rounded-lg p-3"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-white">
                            {window.window_id}
                          </span>
                          <div
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              window.risk_level === "CRITICAL"
                                ? "text-red-400 bg-red-900/20"
                                : window.risk_level === "HIGH"
                                ? "text-orange-400 bg-orange-900/20"
                                : "text-yellow-400 bg-yellow-900/20"
                            }`}
                          >
                            {window.risk_level}
                          </div>
                        </div>
                        <div className="text-sm text-gray-400">
                          {new Date(window.scheduled_time).toLocaleString()} •{" "}
                          {window.estimated_duration}h
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-center">
                <button
                  onClick={() => optimizeMaintenanceWindows(clientId, plan)}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  <Zap className="w-5 h-5 mr-2" />
                  Optimize Maintenance Windows
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Maintenance Tab */}
      {activeTab === "maintenance" && (
        <div className="space-y-6">
          {Object.entries(maintenanceWindows).map(
            ([clientId, optimization]) => (
              <div
                key={clientId}
                className="bg-gray-800 border border-gray-700 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
                    Optimized Maintenance Windows
                  </h3>
                  <div className="text-sm text-gray-400">
                    Success Prediction:{" "}
                    {(optimization.success_prediction * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-md font-medium text-gray-300 mb-3">
                      Optimized Schedule
                    </h4>
                    <div className="space-y-3">
                      {optimization.optimized_windows.map((window, idx) => (
                        <div
                          key={idx}
                          className="bg-gray-700/50 border border-gray-600 rounded-lg p-4"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-white">
                              {window.window_id}
                            </span>
                            <div className="text-sm text-green-400">
                              {(window.success_probability * 100).toFixed(1)}%
                              success
                            </div>
                          </div>
                          <div className="text-sm text-gray-400 mb-2">
                            {new Date(window.optimized_time).toLocaleString()}
                          </div>
                          <div className="text-xs text-gray-500">
                            {window.reasoning}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-md font-medium text-gray-300 mb-3">
                      Risk Assessment
                    </h4>
                    <div className="space-y-3">
                      <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                        <div className="text-sm text-gray-300 mb-2">
                          Overall Risk: {optimization.overall_risk_assessment}
                        </div>
                        <div className="text-sm text-gray-300 mb-2">
                          Approach: {optimization.recommended_approach}
                        </div>
                        <div className="text-sm text-gray-400">
                          Success Prediction:{" "}
                          {(optimization.success_prediction * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}

      {/* Monitoring Tab */}
      {activeTab === "monitoring" && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Patch Execution Monitoring
            </h3>
            <div className="text-center text-gray-400 py-8">
              <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-600" />
              <p>No active patch executions to monitor</p>
              <p className="text-sm mt-2">
                Start a patch execution to see real-time monitoring data
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedPatchManagement;
