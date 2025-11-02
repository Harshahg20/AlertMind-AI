import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  Shield,
  AlertTriangle,
  RefreshCw,
  BarChart3,
  Calendar,
  Zap,
  Target,
  Brain,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";
import { EnhancedPatchSkeleton } from "./SkeletonLoader";

const EnhancedPatchManagement = ({ clients = [], loading = false }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  const [cveDatabase, setCveDatabase] = useState([]);
  const [patchPlans, setPatchPlans] = useState({});
  const [cveAnalyses, setCveAnalyses] = useState({});
  const [maintenanceWindows, setMaintenanceWindows] = useState({});
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("cve-analysis");
  const [selectedCves, setSelectedCves] = useState([]);
  const [analyzingCves, setAnalyzingCves] = useState(new Set());

  // Safe clients array
  const displayClients = clients && Array.isArray(clients) ? clients : [];

  // Optimize loading - only fetch when component mounts and clients available
  const fetchedRef = useRef(false);
  
  useEffect(() => {
    if (displayClients.length > 0 && !fetchedRef.current) {
      fetchedRef.current = true;
      fetchCveDatabase();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [displayClients.length]);

  const fetchCveDatabase = useCallback(async () => {
    try {
      setLoadingData(true);
      setError(null);
      // FastAPI returns data directly, not nested in .data
      const response = await apiClient.get("/enhanced-patch/cve-database");
      const data = response.cve_database || response.data?.cve_database || [];
      setCveDatabase(data);
      if (data.length === 0) {
        setError("No CVEs found. Please check your connection or try refreshing.");
      }
    } catch (err) {
      console.error("Error fetching CVE database:", err);
      setError(err.message || "Failed to load CVE database. Please try again.");
      setCveDatabase([]);
    } finally {
      setLoadingData(false);
    }
  }, []);

  const analyzeCveForClient = useCallback(async (clientId, cveId) => {
    // Skip if already analyzed or currently analyzing
    const key = `${clientId}_${cveId}`;
    if (cveAnalyses[key] || analyzingCves.has(key)) {
      return;
    }
    
    try {
      setAnalyzingCves((prev) => new Set(prev).add(key));
      setError(null);
      const response = await apiClient.get(
        `/enhanced-patch/cve-analysis/${clientId}?cve_id=${cveId}`
      );
      const analysis = response.cve_analysis || response.data?.cve_analysis;
      if (analysis) {
        setCveAnalyses((prev) => ({
          ...prev,
          [key]: analysis,
        }));
      }
    } catch (err) {
      console.error("Error analyzing CVE:", err);
      setError(`Failed to analyze ${cveId}: ${err.message || "Unknown error"}`);
    } finally {
      setAnalyzingCves((prev) => {
        const next = new Set(prev);
        next.delete(key);
        return next;
      });
    }
  }, [cveAnalyses, analyzingCves]);

  const generatePatchPlan = useCallback(async (clientId, cveList) => {
    if (!clientId || cveList.length === 0) return;
    
    try {
      setLoadingData(true);
      setError(null);
      console.log("Generating patch plan for:", clientId, "with CVEs:", cveList);
      const response = await apiClient.post(
        `/enhanced-patch/patch-plan/${clientId}`,
        cveList
      );
      console.log("Patch plan response:", response);
      const plan = response.patch_plan || response.data?.patch_plan;
      if (plan) {
        console.log("Setting patch plan:", plan);
        setPatchPlans((prev) => ({
          ...prev,
          [clientId]: plan,
        }));
        setActiveTab("patch-plan"); // Switch to patch plan tab
      } else {
        console.error("No patch_plan in response:", response);
        setError("Patch plan generation succeeded but returned no data. Please try again.");
      }
    } catch (err) {
      console.error("Error generating patch plan:", err);
      setError(`Failed to generate patch plan: ${err.message || "Unknown error"}`);
    } finally {
      setLoadingData(false);
    }
  }, []);

  const generateSamplePatchPlan = useCallback(async () => {
    if (displayClients.length === 0) return;
    const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
    if (!clientId) return;

    try {
      setLoadingData(true);
      setError(null);
      
      // Use first 3 CVEs from database as sample
      const sampleCves = cveDatabase.slice(0, 3).map(cve => ({
        cve_id: cve.cve || cve.cve_id,
        severity: cve.severity,
        product: cve.product,
        summary: cve.summary
      }));

      if (sampleCves.length === 0) {
        setError("No CVEs available. Please load the CVE database first.");
        return;
      }

      console.log("Generating sample patch plan for:", clientId, "with CVEs:", sampleCves);
      const response = await apiClient.post(
        `/enhanced-patch/patch-plan/${clientId}`,
        sampleCves
      );
      console.log("Sample patch plan response:", response);
      const plan = response.patch_plan || response.data?.patch_plan;
      if (plan) {
        console.log("Setting sample patch plan:", plan);
        setPatchPlans((prev) => ({
          ...prev,
          [clientId]: plan,
        }));
        setActiveTab("patch-plan"); // Switch to patch plan tab
      } else {
        console.error("No patch_plan in response:", response);
        setError("Patch plan generation succeeded but returned no data. Please try again.");
      }
    } catch (err) {
      console.error("Error generating sample patch plan:", err);
      setError(`Failed to generate sample patch plan: ${err.message || "Unknown error"}`);
    } finally {
      setLoadingData(false);
    }
  }, [displayClients, selectedClient, cveDatabase]);

  const optimizeMaintenanceWindows = useCallback(async (clientId, patchPlan) => {
    try {
      setLoadingData(true);
      setError(null);
      const response = await apiClient.post(
        `/enhanced-patch/optimize-maintenance/${clientId}`,
        patchPlan
      );
      const optimization = response.optimization || response.data?.optimization;
      if (optimization) {
        setMaintenanceWindows((prev) => ({
          ...prev,
          [clientId]: optimization,
        }));
        setActiveTab("maintenance");
      }
    } catch (err) {
      console.error("Error optimizing maintenance windows:", err);
      setError(`Failed to optimize maintenance windows: ${err.message || "Unknown error"}`);
    } finally {
      setLoadingData(false);
    }
  }, []);

  // Auto-populate maintenance windows when patch plan is generated
  useEffect(() => {
    if (Object.keys(patchPlans).length > 0) {
      // Copy maintenance windows from patch plans to maintenance tab state
      const newMaintenanceWindows = {};
      Object.entries(patchPlans).forEach(([clientId, plan]) => {
        if (plan.maintenance_windows && plan.maintenance_windows.length > 0) {
          // Convert patch plan maintenance windows to optimization format
          newMaintenanceWindows[clientId] = {
            success_prediction: 0.85,
            optimized_windows: plan.maintenance_windows.map((window, idx) => ({
              window_id: window.window_id || `window_${idx + 1}`,
              scheduled_time: window.scheduled_time,
              estimated_duration: window.estimated_duration || 2,
              risk_level: window.risk_level || "MEDIUM",
              cve_ids: window.cve_ids || [],
              patches: window.patches || [],
              rollback_plan: window.rollback_plan || {},
              optimization_reason: `Scheduled based on patch priority and risk assessment`,
              recommended_actions: [
                "Perform pre-patch backup",
                "Verify system health before maintenance",
                "Monitor during deployment"
              ]
            })),
            overall_risk: plan.maintenance_windows.length > 0 
              ? plan.maintenance_windows[0].risk_level || "MEDIUM" 
              : "MEDIUM",
            estimated_total_downtime: plan.maintenance_windows.reduce(
              (sum, w) => sum + (w.estimated_duration || 0), 0
            )
          };
        }
      });
      
      // Only update if we have new maintenance windows and they're different
      if (Object.keys(newMaintenanceWindows).length > 0) {
        setMaintenanceWindows((prev) => ({
          ...prev,
          ...newMaintenanceWindows,
        }));
      }
    }
  }, [patchPlans]);


  const handleCveSelection = (cveId, selected) => {
    if (selected) {
      setSelectedCves((prev) => [...prev, cveId]);
    } else {
      setSelectedCves((prev) => prev.filter((id) => id !== cveId));
    }
  };

  const handleGeneratePatchPlan = async () => {
    const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
    if (!clientId || selectedCves.length === 0) return;

    const selectedCveData = cveDatabase.filter((cve) =>
      selectedCves.includes(cve.cve || cve.cve_id)
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

  // Show skeleton only on initial load, not during data updates
  if (loading && cveDatabase.length === 0) {
    return <EnhancedPatchSkeleton />;
  }

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
            disabled={loadingData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loadingData ? "animate-spin" : ""}`} />
            {loadingData ? "Loading..." : "Refresh"}
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
            {displayClients.map((client) => (
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

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-300">{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-300"
          >
            ×
          </button>
        </div>
      )}

      {/* CVE Analysis Tab */}
      {activeTab === "cve-analysis" && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-red-400" />
                CVE Database Analysis
              </h3>
              <div className="flex items-center space-x-4">
                {loadingData && (
                  <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                )}
                <div className="text-sm text-gray-400">
                  {cveDatabase.length} CVEs available
                </div>
              </div>
            </div>

            {cveDatabase.length === 0 && !loadingData ? (
              <div className="text-center py-12">
                <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p className="text-gray-400 mb-2">No CVEs found</p>
                <p className="text-sm text-gray-500 mb-4">
                  {error || "Click refresh to load CVE database"}
                </p>
                <button
                  onClick={fetchCveDatabase}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  Load CVEs
                </button>
              </div>
            ) : (
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
                            ? displayClients[0]?.id
                            : selectedClient,
                          cve.cve
                        )
                      }
                      disabled={analyzingCves.has(`${selectedClient === "all" ? displayClients[0]?.id : selectedClient}_${cve.cve}`) || !displayClients.length}
                      className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:opacity-50 text-white text-xs rounded transition-colors flex items-center justify-center"
                    >
                      {analyzingCves.has(`${selectedClient === "all" ? displayClients[0]?.id : selectedClient}_${cve.cve}`) ? (
                        <>
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          {cveAnalyses[`${selectedClient === "all" ? displayClients[0]?.id : selectedClient}_${cve.cve}`] && (
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                          )}
                          {cveAnalyses[`${selectedClient === "all" ? displayClients[0]?.id : selectedClient}_${cve.cve}`] ? "Re-analyze" : "Analyze"}
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
              </div>
            )}

            {selectedCves.length > 0 && (
              <div className="mt-6 flex justify-center">
                <button
                  onClick={handleGeneratePatchPlan}
                  disabled={loadingData || !displayClients.length}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  {loadingData ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Target className="w-5 h-5 mr-2" />
                      Generate Patch Plan ({selectedCves.length} CVEs)
                    </>
                  )}
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
          {Object.keys(patchPlans).length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Target className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No patch plans generated yet</p>
              <p className="text-sm text-gray-500 mb-6">
                Generate a sample patch plan automatically or select CVEs from the CVE Analysis tab
              </p>
              <div className="flex justify-center gap-4">
                <button
                  onClick={generateSamplePatchPlan}
                  disabled={loadingData || displayClients.length === 0 || cveDatabase.length === 0}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  {loadingData ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Generate Sample Patch Plan
                    </>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab("cve-analysis")}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  <Target className="w-5 h-5 mr-2" />
                  Go to CVE Analysis
                </button>
              </div>
            </div>
          ) : (
            Object.entries(patchPlans).map(([clientId, plan]) => (
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
                    {plan.cve_analyses && plan.cve_analyses.length > 0 ? (
                      plan.cve_analyses.map((analysis, idx) => (
                        <div
                          key={idx}
                          className="bg-gray-700/50 border border-gray-600 rounded-lg p-3"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-mono text-sm text-blue-400">
                              {analysis.cve_id || `CVE-${idx + 1}`}
                            </span>
                            <div
                              className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                                analysis.patch_priority
                              )}`}
                            >
                              {analysis.patch_priority || "LOW"}
                            </div>
                          </div>
                          <div className="text-sm text-gray-400">
                            {analysis.product || "Unknown"} • Impact:{" "}
                            {analysis.client_impact 
                              ? `${(analysis.client_impact * 100).toFixed(1)}%`
                              : "N/A"}
                          </div>
                          {analysis.estimated_effort && (
                            <div className="text-xs text-gray-500 mt-1">
                              Effort: {analysis.estimated_effort.hours || 0}h
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-400 py-4 text-sm">
                        No CVE analyses available
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="text-md font-medium text-gray-300 mb-3">
                    Maintenance Windows
                  </h4>
                  <div className="space-y-3">
                    {plan.maintenance_windows && plan.maintenance_windows.length > 0 ? (
                      plan.maintenance_windows.map((window, idx) => (
                        <div
                          key={idx}
                          className="bg-gray-700/50 border border-gray-600 rounded-lg p-3"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-white">
                              {window.window_id || `Window ${idx + 1}`}
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
                              {window.risk_level || "MEDIUM"}
                            </div>
                          </div>
                          <div className="text-sm text-gray-400 mb-1">
                            {window.scheduled_time ? (
                              new Date(window.scheduled_time).toLocaleString()
                            ) : (
                              "Time TBD"
                            )}{" "}
                            • {window.estimated_duration || 0}h
                          </div>
                          {window.cve_ids && window.cve_ids.length > 0 && (
                            <div className="text-xs text-gray-500 mt-1">
                              CVEs: {window.cve_ids.join(", ")}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-400 py-4 text-sm">
                        No maintenance windows scheduled yet
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-center">
                <button
                  onClick={() => optimizeMaintenanceWindows(clientId, plan)}
                  disabled={loadingData}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  {loadingData ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Optimizing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Optimize Maintenance Windows
                    </>
                  )}
                </button>
              </div>
            </div>
            ))
          )}
        </div>
      )}

      {/* Maintenance Tab */}
      {activeTab === "maintenance" && (
        <div className="space-y-6">
          {Object.keys(maintenanceWindows).length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No optimized maintenance windows</p>
              <p className="text-sm text-gray-500 mb-6">
                Generate a patch plan first to see maintenance windows, or generate a sample one
              </p>
              <div className="flex justify-center gap-4">
                <button
                  onClick={generateSamplePatchPlan}
                  disabled={loadingData || displayClients.length === 0 || cveDatabase.length === 0}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  {loadingData ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Generate Sample Patch Plan
                    </>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab("patch-plan")}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors flex items-center"
                >
                  <Target className="w-5 h-5 mr-2" />
                  Go to Patch Plan
                </button>
              </div>
            </div>
          ) : (
            Object.entries(maintenanceWindows).map(
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
                      {(optimization.optimized_windows || []).map((window, idx) => (
                        <div
                          key={idx}
                          className="bg-gray-700/50 border border-gray-600 rounded-lg p-4"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-white">
                              {window.window_id || `Window ${idx + 1}`}
                            </span>
                            <div className={`px-2 py-1 rounded text-xs font-medium ${
                              window.risk_level === "CRITICAL" ? "text-red-400 bg-red-900/20" :
                              window.risk_level === "HIGH" ? "text-orange-400 bg-orange-900/20" :
                              "text-yellow-400 bg-yellow-900/20"
                            }`}>
                              {window.risk_level || "MEDIUM"}
                            </div>
                          </div>
                          <div className="text-sm text-gray-400 mb-2">
                            {window.scheduled_time || window.optimized_time ? (
                              new Date(window.scheduled_time || window.optimized_time).toLocaleString()
                            ) : (
                              "Time TBD"
                            )}
                            {" • "}
                            {window.estimated_duration || 0}h duration
                          </div>
                          {window.cve_ids && window.cve_ids.length > 0 && (
                            <div className="text-xs text-gray-500 mb-2">
                              CVEs: {window.cve_ids.join(", ")}
                            </div>
                          )}
                          <div className="text-xs text-gray-500">
                            {window.optimization_reason || window.reasoning || "Scheduled maintenance window"}
                          </div>
                          {window.recommended_actions && window.recommended_actions.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {window.recommended_actions.map((action, actionIdx) => (
                                <div key={actionIdx} className="text-xs text-gray-400">
                                  • {action}
                                </div>
                              ))}
                            </div>
                          )}
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
                          Overall Risk: {optimization.overall_risk || optimization.overall_risk_assessment || "MEDIUM"}
                        </div>
                        {optimization.recommended_approach && (
                          <div className="text-sm text-gray-300 mb-2">
                            Approach: {optimization.recommended_approach}
                          </div>
                        )}
                        <div className="text-sm text-gray-400 mb-2">
                          Success Prediction:{" "}
                          {((optimization.success_prediction || 0.85) * 100).toFixed(1)}%
                        </div>
                        {optimization.estimated_total_downtime !== undefined && (
                          <div className="text-sm text-gray-400">
                            Estimated Total Downtime: {optimization.estimated_total_downtime}h
                          </div>
                        )}
                      </div>
                      {optimization.optimized_windows && optimization.optimized_windows.length > 0 && (
                        <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-gray-300 mb-2">
                            Maintenance Summary
                          </h5>
                          <div className="text-xs text-gray-400 space-y-1">
                            <div>Total Windows: {optimization.optimized_windows.length}</div>
                            <div>
                              Total Patches: {optimization.optimized_windows.reduce(
                                (sum, w) => sum + (w.cve_ids?.length || 0), 0
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
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
