import React, { useState, useEffect, useCallback, useRef, useMemo } from "react";
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
  Building,
  Activity,
  CheckCircle,
  Server,
  Clock,
  Network,
  Terminal,
  Sparkles,
  TrendingDown,
  Users,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";
import { EnhancedPatchSkeleton } from "./SkeletonLoader";

const EnhancedPatchManagement = ({ clients = [], loading = false, remediationContext = null }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  const [cveDatabase, setCveDatabase] = useState([]);
  const [patchPlans, setPatchPlans] = useState({});
  const [cveAnalyses, setCveAnalyses] = useState({});
  const [maintenanceWindows, setMaintenanceWindows] = useState({});
  const [companyReports, setCompanyReports] = useState(null);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(remediationContext ? "remediation" : "cve-analysis");
  const [selectedCves, setSelectedCves] = useState([]);
  const [analyzingCves, setAnalyzingCves] = useState(new Set());
  const [monitoringData, setMonitoringData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [executionReadiness, setExecutionReadiness] = useState(null);
  const [loadingReadiness, setLoadingReadiness] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Safe clients array
  const displayClients = clients && Array.isArray(clients) ? clients : [];

  // Filter CVEs based on selected client to simulate different environments
  const displayCves = useMemo(() => {
    if (selectedClient === "all") return cveDatabase;
    
    const client = displayClients.find(c => c.id === selectedClient);
    if (!client) return cveDatabase;

    // Deterministic filtering based on client ID and CVE ID
    return cveDatabase.filter(cve => {
      const cveHash = cve.cve.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      const clientHash = client.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      // Show subset of CVEs (approx 60-70%) that varies by client
      return (cveHash + clientHash) % 3 !== 0;
    });
  }, [selectedClient, cveDatabase, displayClients]);

  // Optimize loading - only fetch when component mounts and clients available
  const fetchedRef = useRef(false);
  
  useEffect(() => {
    if (displayClients.length > 0 && !fetchedRef.current) {
      fetchedRef.current = true;
      fetchCveDatabase();
    }
  }, [displayClients.length]);

  // Handle Remediation Context
  useEffect(() => {
    if (remediationContext) {
      setActiveTab("remediation");
      // Auto-select the client from the context if available
      if (remediationContext.client) {
        const client = displayClients.find(c => c.name === remediationContext.client || c.id === remediationContext.client);
        if (client) {
          setSelectedClient(client.id);
        }
      }
    }
  }, [remediationContext, displayClients]);

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

  const fetchCompanyReports = useCallback(async () => {
    try {
      setLoadingData(true);
      setError(null);
      const response = await apiClient.get("/enhanced-patch/company-patch-reports");
      const data = response.reports || response.data?.reports || [];
      setCompanyReports(data);
    } catch (err) {
      console.error("Error fetching company reports:", err);
      setError(err.message || "Failed to load company reports.");
    } finally {
      setLoadingData(false);
    }
  }, []);

  const fetchMonitoringSimulation = useCallback(async () => {
    try {
      setLoadingData(true);
      setError(null);
      const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
      if (!clientId) return;
      
      const response = await apiClient.post(`/enhanced-patch/monitor-simulation/${clientId}`);
      const data = response.simulation_data || response.data?.simulation_data;
      setMonitoringData(data);
    } catch (err) {
      console.error("Error fetching monitoring simulation:", err);
      setError(err.message || "Failed to load monitoring data.");
    } finally {
      setLoadingData(false);
    }
  }, [selectedClient, displayClients]);

  const fetchExecutionReadiness = useCallback(async (clientId, patchPlan) => {
    try {
      setLoadingReadiness(true);
      setError(null);
      
      const response = await apiClient.post(`/enhanced-patch/execution-readiness/${clientId}`, patchPlan);
      const data = response.execution_readiness || response.data?.execution_readiness;
      setExecutionReadiness(data);
    } catch (err) {
      console.error("Error fetching execution readiness:", err);
      setError(err.message || "Failed to load execution readiness.");
    } finally {
      setLoadingReadiness(false);
    }
  }, []);

  const handleExecutePatchDeployment = useCallback(async (targetClientId) => {
    setIsExecuting(true);
    // Switch to monitoring tab
    setActiveTab("monitoring");
    
    // Use targetClientId if provided, otherwise fallback to selectedClient logic
    const clientId = targetClientId || (selectedClient === "all" ? displayClients[0]?.id : selectedClient);
    
    if (clientId) {
      // Update selected client if we are in 'all' view so the monitoring tab shows the right one
      if (selectedClient === "all") {
        setSelectedClient(clientId);
      }
      await fetchMonitoringSimulation();
    }
    setIsExecuting(false);
  }, [selectedClient, displayClients, fetchMonitoringSimulation, setActiveTab]);

  const handleSimulateRollback = async () => {
    setIsExecuting(true);
    setActiveTab("monitoring");
    // In a real app, we would call a specific rollback endpoint
    // For demo, we'll re-use the monitoring simulation but with a "Rollback" context
    const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
    if (clientId) {
      await fetchMonitoringSimulation();
    }
    
    // Simulate completion after 5 seconds (approx time of simulation)
    setTimeout(() => {
      setIsExecuting(false);
      setShowSuccess(true);
    }, 5000);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

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
            onChange={(e) => {
              setSelectedClient(e.target.value);
              setSelectedCves([]); // Clear selection when changing client
              setExecutionReadiness(null); // Clear execution readiness
              setMonitoringData(null); // Clear monitoring data
            }}
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
            { id: "company-reports", label: "Company Reports", icon: Building },
            { id: "monitoring", label: "Monitoring", icon: BarChart3 },
            ...(remediationContext ? [{ id: "remediation", label: "Incident Response", icon: AlertTriangle }] : []),
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                if (tab.id === "company-reports" && !companyReports) {
                  fetchCompanyReports();
                }
              }}
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
              <div className="flex flex-col">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-red-400" />
                  CVE Database Analysis
                  <div className="ml-4 px-2 py-0.5 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-full flex items-center">
                    <Sparkles className="w-3 h-3 text-blue-400 mr-1" />
                    <span className="text-[10px] font-medium text-blue-300">Powered by Gemini 1.5 Flash</span>
                  </div>
                </h3>
                {selectedClient !== "all" && (
                  <span className="text-xs text-blue-400 ml-7 mt-1">
                    Displaying relevant CVEs for {displayClients.find(c => c.id === selectedClient)?.name} environment
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-4">
                {loadingData && (
                  <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                )}
                <div className="text-sm text-gray-400">
                  {displayCves.length} CVEs available
                </div>
              </div>
            </div>

            {displayCves.length === 0 && !loadingData ? (
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
              {displayCves.map((cve) => (
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
                {Object.entries(cveAnalyses)
                  .filter(([key]) => selectedClient === "all" || key.startsWith(`${selectedClient}_`))
                  .map(([key, analysis]) => (
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

                    <div className="mb-4 bg-blue-900/20 border border-blue-800 rounded-lg p-3">
                      <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-1">Executive Summary</h4>
                      <p className="text-sm text-gray-300">
                        {analysis.ai_analysis?.executive_summary || "Analysis pending..."}
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">
                          AI Analysis
                        </h4>
                        <div className="space-y-2 text-sm text-gray-400">
                          <div className="flex justify-between items-center">
                            <span>Impact Score:</span>
                            <span className="text-white font-mono">{(analysis.client_impact * 100).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span>Business Impact:</span>
                            <span className={`uppercase text-xs font-bold px-2 py-0.5 rounded ${
                              analysis.ai_analysis?.business_impact === 'critical' ? 'bg-red-900/50 text-red-400' : 'bg-gray-700 text-gray-300'
                            }`}>
                              {analysis.ai_analysis?.business_impact || "N/A"}
                            </span>
                          </div>
                          
                          {/* Probability of Exploitation */}
                          <div className="pt-2">
                            <div className="flex justify-between text-xs mb-1">
                              <span>Exploit Probability</span>
                              <span className="text-red-400">{analysis.ai_analysis?.probability_of_exploitation_percentage || 0}%</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-1.5">
                              <div 
                                className="bg-red-500 h-1.5 rounded-full" 
                                style={{ width: `${analysis.ai_analysis?.probability_of_exploitation_percentage || 0}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Compliance Badges */}
                          {analysis.ai_analysis?.compliance_badges && analysis.ai_analysis.compliance_badges.length > 0 && (
                            <div className="pt-2">
                              <span className="text-xs text-gray-500 block mb-1">Compliance Risks:</span>
                              <div className="flex flex-wrap gap-1">
                                {analysis.ai_analysis.compliance_badges.map((badge, i) => (
                                  <span key={i} className="text-xs bg-purple-900/30 text-purple-300 border border-purple-700/50 px-1.5 py-0.5 rounded">
                                    {badge}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Blast Radius */}
                          {analysis.ai_analysis?.blast_radius_details && (
                            <div className="pt-2 mt-2 border-t border-gray-700">
                              <span className="text-xs text-gray-500 block mb-1">Blast Radius:</span>
                              <div className="text-xs text-gray-400">
                                <div className="flex items-start mb-1">
                                  <span className="text-red-400 mr-1">• Direct:</span>
                                  <span>{analysis.ai_analysis.blast_radius_details.direct_affected_systems?.join(", ") || "None"}</span>
                                </div>
                                <div className="flex items-start">
                                  <span className="text-orange-400 mr-1">• Indirect:</span>
                                  <span>{analysis.ai_analysis.blast_radius_details.indirect_affected_systems?.join(", ") || "None"}</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">
                          Detailed Recommendations
                        </h4>
                        <div className="space-y-2">
                          {analysis.ai_analysis?.detailed_recommendation_steps ? (
                            analysis.ai_analysis.detailed_recommendation_steps.map((step, idx) => (
                              <div key={idx} className="text-sm text-gray-400 bg-gray-800/50 p-2 rounded border border-gray-700">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="font-medium text-blue-300">{step.step}</span>
                                  <span className="text-xs text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded">{step.estimated_time}</span>
                                </div>
                                <p className="text-xs text-gray-500">{step.description}</p>
                              </div>
                            ))
                          ) : (
                            analysis.ai_analysis?.recommended_actions
                              ?.slice(0, 3)
                              .map((action, idx) => (
                                <div key={idx} className="text-sm text-gray-400">
                                  • {action}
                                </div>
                              ))
                          )}
                        </div>
                        {analysis.ai_analysis?.realistic_implementation_time_hours && (
                          <div className="mt-3 text-xs text-gray-400 flex items-center">
                            <Calendar className="w-3 h-3 mr-1 text-blue-400" />
                            Realistic Implementation: <span className="text-white ml-1">{analysis.ai_analysis.realistic_implementation_time_hours} hours</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Business & Financial Impact Section */}
                    <div className="mt-4 pt-4 border-t border-gray-600 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                          <BarChart3 className="w-4 h-4 mr-2 text-green-400" />
                          Business Impact & ROI
                        </h4>
                        <div className="space-y-1 text-sm text-gray-400">
                          <div className="flex justify-between">
                            <span>Revenue at Risk:</span>
                            <span className="text-red-400 font-mono">
                              {analysis.business_impact?.revenue_at_risk_usd 
                                ? `$${analysis.business_impact.revenue_at_risk_usd.toLocaleString()}` 
                                : "Calculating..."}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>ROI Ratio:</span>
                            <span className="text-green-400 font-mono">
                              {analysis.business_impact?.cost_benefit_analysis?.roi_ratio 
                                ? `${analysis.business_impact.cost_benefit_analysis.roi_ratio}:1` 
                                : "N/A"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Affected Users:</span>
                            <span className="text-blue-400 font-mono">
                              {analysis.business_impact?.affected_users_estimate || "N/A"}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                          <Brain className="w-4 h-4 mr-2 text-purple-400" />
                          AI Financial Assessment
                        </h4>
                        <div className="space-y-1 text-sm text-gray-400">
                          <div>
                            <span className="text-gray-500">Est. Exploit Cost:</span>{" "}
                            {analysis.ai_analysis?.financial_impact_analysis?.estimated_cost_of_exploitation || "N/A"}
                          </div>
                          <div>
                            <span className="text-gray-500">Patch ROI:</span>{" "}
                            {analysis.ai_analysis?.financial_impact_analysis?.patching_roi || "N/A"}
                          </div>
                          <div>
                            <span className="text-gray-500">Op. Risk Score:</span>{" "}
                            {analysis.ai_analysis?.financial_impact_analysis?.operational_risk_score || "N/A"}
                          </div>
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
            Object.entries(patchPlans)
              .filter(([clientId]) => selectedClient === "all" || clientId === selectedClient)
              .map(([clientId, plan]) => (
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
            Object.entries(maintenanceWindows)
              .filter(([clientId]) => selectedClient === "all" || clientId === selectedClient)
              .map(
              ([clientId, optimization]) => (
              <div
                key={clientId}
                className="bg-gray-800 border border-gray-700 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
                    Optimized Maintenance Windows
                  </h3>
                  <div className="flex items-center space-x-3">
                    <div className="text-sm text-gray-400">
                      Success Prediction:{" "}
                      {(optimization.success_prediction * 100).toFixed(1)}%
                    </div>
                    <button
                      onClick={() => fetchExecutionReadiness(clientId, patchPlans[clientId])}
                      disabled={loadingReadiness}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                    >
                      {loadingReadiness ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Check Execution Readiness
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Execution Readiness Panel */}
                {executionReadiness && (
                  <div className="mb-6 bg-gradient-to-r from-green-900/20 to-blue-900/20 border-2 border-green-600/50 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${
                          executionReadiness.readiness_status === 'READY' ? 'bg-green-900/50' :
                          executionReadiness.readiness_status === 'CAUTION' ? 'bg-yellow-900/50' : 'bg-red-900/50'
                        }`}>
                          <CheckCircle className={`w-6 h-6 ${
                            executionReadiness.readiness_status === 'READY' ? 'text-green-400' :
                            executionReadiness.readiness_status === 'CAUTION' ? 'text-yellow-400' : 'text-red-400'
                          }`} />
                        </div>
                        <div>
                          <h4 className="text-lg font-bold text-white">Execution Readiness Analysis</h4>
                          <p className={`text-sm ${
                            executionReadiness.readiness_status === 'READY' ? 'text-green-400' :
                            executionReadiness.readiness_status === 'CAUTION' ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {executionReadiness.recommended_action}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-white">{executionReadiness.readiness_score}%</div>
                        <div className="text-xs text-gray-400 uppercase tracking-wider">Readiness Score</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                      {/* Pre-Flight Checks */}
                      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400 uppercase tracking-wider">System Health</span>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        </div>
                        <div className="text-sm text-white font-medium">
                          {executionReadiness.pre_flight_validation.system_health.checks.filter(c => c.status === 'PASS').length}/
                          {executionReadiness.pre_flight_validation.system_health.checks.length} Checks Pass
                        </div>
                      </div>

                      {/* Backup Status */}
                      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400 uppercase tracking-wider">Backup Status</span>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        </div>
                        <div className="text-sm text-white font-medium">
                          {executionReadiness.pre_flight_validation.backup_status.backup_size}
                        </div>
                        <div className="text-xs text-gray-500">2 hours ago</div>
                      </div>

                      {/* Rollback Time */}
                      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400 uppercase tracking-wider">Rollback Time</span>
                          <Clock className="w-4 h-4 text-blue-400" />
                        </div>
                        <div className="text-sm text-white font-medium">
                          {executionReadiness.rollback_plan.total_rollback_time_minutes} min
                        </div>
                        <div className="text-xs text-gray-500">{executionReadiness.rollback_plan.rollback_success_rate} success rate</div>
                      </div>

                      {/* Team Ready */}
                      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400 uppercase tracking-wider">Team Status</span>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        </div>
                        <div className="text-sm text-white font-medium">
                          {executionReadiness.team_assignments.primary_team.members.length + 1} Members
                        </div>
                        <div className="text-xs text-gray-500">On-call ready</div>
                      </div>
                    </div>

                    {/* Detailed Expandable Sections */}
                    <div className="space-y-3">
                      {/* System Health Details */}
                      <div className="bg-gray-800/30 rounded-lg border border-gray-700 overflow-hidden">
                        <button
                          onClick={() => toggleSection('systemHealth')}
                          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
                        >
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-400" />
                            <span className="text-sm font-semibold text-white">System Health Checks (4/4 Passed)</span>
                          </div>
                          <span className="text-gray-400">{expandedSections.systemHealth ? '▼' : '▶'}</span>
                        </button>
                        {expandedSections.systemHealth && (
                          <div className="px-4 pb-4 space-y-2">
                            {executionReadiness.pre_flight_validation.system_health.checks.map((check, idx) => (
                              <div key={idx} className="flex items-center justify-between bg-gray-900/50 rounded p-2">
                                <div className="flex items-center space-x-2">
                                  <CheckCircle className="w-3 h-3 text-green-400" />
                                  <span className="text-xs text-white">{check.name}</span>
                                </div>
                                <div className="flex items-center space-x-3">
                                  <span className="text-xs text-gray-400">{check.value}</span>
                                  <span className="text-xs text-gray-500">Threshold: {check.threshold}</span>
                                  <span className="text-xs px-2 py-0.5 rounded bg-green-900/30 text-green-400">{check.status}</span>
                                </div>
                              </div>
                            ))}
                            <div className="mt-3 p-3 bg-blue-900/20 border border-blue-800 rounded">
                              <div className="text-xs font-semibold text-blue-400 mb-1">Dependency Services Status</div>
                              <div className="grid grid-cols-2 gap-2">
                                {executionReadiness.pre_flight_validation.dependency_services.services.map((svc, idx) => (
                                  <div key={idx} className="flex items-center justify-between text-xs">
                                    <span className="text-gray-300">{svc.name}</span>
                                    <span className="text-green-400">{svc.status} ({svc.version})</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Rollback Plan Details */}
                      <div className="bg-gray-800/30 rounded-lg border border-gray-700 overflow-hidden">
                        <button
                          onClick={() => toggleSection('rollbackPlan')}
                          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
                        >
                          <div className="flex items-center space-x-2">
                            <AlertTriangle className="w-4 h-4 text-yellow-400" />
                            <span className="text-sm font-semibold text-white">Automated Rollback Plan (15 min, 98.5% success)</span>
                          </div>
                          <span className="text-gray-400">{expandedSections.rollbackPlan ? '▼' : '▶'}</span>
                        </button>
                        {expandedSections.rollbackPlan && (
                          <div className="px-4 pb-4 space-y-2">
                            {executionReadiness.rollback_plan.rollback_steps.map((step, idx) => (
                              <div key={idx} className="flex items-start space-x-3 bg-gray-900/50 rounded p-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-900/50 border border-blue-600 flex items-center justify-center text-xs text-blue-400 font-bold">
                                  {step.step}
                                </div>
                                <div className="flex-1">
                                  <div className="text-sm text-white font-medium mb-1">{step.action}</div>
                                  <div className="grid grid-cols-2 gap-2 text-xs">
                                    <div><span className="text-gray-500">Duration:</span> <span className="text-blue-400">{step.duration_minutes} min</span></div>
                                    <div><span className="text-gray-500">Automated:</span> <span className="text-green-400">{step.automated ? 'Yes' : 'No'}</span></div>
                                    <div><span className="text-gray-500">Responsible:</span> <span className="text-white">{step.responsible}</span></div>
                                    {step.trigger && <div><span className="text-gray-500">Trigger:</span> <span className="text-orange-400">{step.trigger}</span></div>}
                                    {step.command && <div className="col-span-2"><span className="text-gray-500">Command:</span> <code className="text-purple-400 font-mono text-xs">{step.command}</code></div>}
                                  </div>
                                </div>
                              </div>
                            ))}
                            <div className="mt-3 p-3 bg-yellow-900/20 border border-yellow-800 rounded">
                              <div className="text-xs font-semibold text-yellow-400 mb-2">Emergency Contact</div>
                              <div className="text-sm text-white font-mono">{executionReadiness.rollback_plan.emergency_contact}</div>
                              <div className="text-xs text-gray-400 mt-1">Last rollback test: {new Date(executionReadiness.rollback_plan.last_rollback_test).toLocaleDateString()}</div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Team Assignments */}
                      <div className="bg-gray-800/30 rounded-lg border border-gray-700 overflow-hidden">
                        <button
                          onClick={() => toggleSection('teamAssignments')}
                          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
                        >
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-400" />
                            <span className="text-sm font-semibold text-white">Team Assignments & Escalation Path</span>
                          </div>
                          <span className="text-gray-400">{expandedSections.teamAssignments ? '▼' : '▶'}</span>
                        </button>
                        {expandedSections.teamAssignments && (
                          <div className="px-4 pb-4 space-y-3">
                            <div className="bg-green-900/20 border border-green-800 rounded p-3">
                              <div className="text-xs font-semibold text-green-400 mb-2">Primary Team</div>
                              <div className="space-y-1 text-xs">
                                <div><span className="text-gray-400">Lead:</span> <span className="text-white font-medium">{executionReadiness.team_assignments.primary_team.lead}</span></div>
                                <div><span className="text-gray-400">Members:</span> <span className="text-white">{executionReadiness.team_assignments.primary_team.members.join(", ")}</span></div>
                                <div><span className="text-gray-400">On-Call:</span> <span className="text-green-400 font-mono">{executionReadiness.team_assignments.primary_team.on_call}</span></div>
                                <div><span className="text-gray-400">Slack:</span> <span className="text-blue-400">{executionReadiness.team_assignments.primary_team.slack_channel}</span></div>
                              </div>
                            </div>
                            <div className="bg-blue-900/20 border border-blue-800 rounded p-3">
                              <div className="text-xs font-semibold text-blue-400 mb-2">Escalation Path</div>
                              <div className="space-y-2">
                                {executionReadiness.team_assignments.escalation_path.map((level, idx) => (
                                  <div key={idx} className="flex items-center justify-between bg-gray-900/50 rounded p-2">
                                    <div className="flex items-center space-x-2">
                                      <div className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">{level.level}</div>
                                      <span className="text-white text-xs">{level.role}</span>
                                    </div>
                                    <span className="text-xs text-gray-400">Response: {level.response_time}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Success Criteria */}
                      <div className="bg-gray-800/30 rounded-lg border border-gray-700 overflow-hidden">
                        <button
                          onClick={() => toggleSection('successCriteria')}
                          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
                        >
                          <div className="flex items-center space-x-2">
                            <Target className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-semibold text-white">Success Criteria & Validation ({executionReadiness.success_criteria.automated_checks.length} automated checks)</span>
                          </div>
                          <span className="text-gray-400">{expandedSections.successCriteria ? '▼' : '▶'}</span>
                        </button>
                        {expandedSections.successCriteria && (
                          <div className="px-4 pb-4 space-y-3">
                            <div className="text-xs text-gray-400 mb-2">Automated Validation Checks:</div>
                            {executionReadiness.success_criteria.automated_checks.map((check, idx) => (
                              <div key={idx} className="bg-gray-900/50 rounded p-2">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-xs font-medium text-white">{check.check}</span>
                                  <span className="text-xs text-green-400">{check.expected}</span>
                                </div>
                                <div className="text-xs text-gray-500">
                                  Method: {check.method} {check.endpoint && `(${check.endpoint})`} • Timeout: {check.timeout || check.window || 'N/A'}
                                </div>
                              </div>
                            ))}
                            <div className="mt-3 p-3 bg-purple-900/20 border border-purple-800 rounded">
                              <div className="text-xs font-semibold text-purple-400 mb-2">Acceptance Threshold</div>
                              <div className="text-xs text-white">{executionReadiness.success_criteria.acceptance_threshold}</div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Execute Button */}
                    {executionReadiness.can_execute_now && (
                      <div className="mt-6 flex justify-center">
                        <button 
                          onClick={() => handleExecutePatchDeployment(clientId)}
                          disabled={isExecuting}
                          className="px-8 py-4 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white rounded-lg font-bold text-lg transition-all transform hover:scale-105 disabled:scale-100 flex items-center shadow-lg"
                        >
                          {isExecuting ? (
                            <>
                              <Loader2 className="w-6 h-6 mr-3 animate-spin" />
                              Starting Deployment...
                            </>
                          ) : (
                            <>
                              <Zap className="w-6 h-6 mr-3" />
                              Execute Patch Deployment Now
                              <CheckCircle className="w-6 h-6 ml-3" />
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                )}

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
                            <div className="px-2 py-0.5 bg-purple-900/30 border border-purple-500/30 rounded text-[10px] text-purple-300 flex items-center ml-2 mr-auto">
                              <Brain className="w-3 h-3 mr-1" />
                              AI Optimized
                            </div>
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
                    
                    {/* Smart Schedule Timeline & Conflicts */}
                    {optimization.conflicts_avoided && optimization.conflicts_avoided.length > 0 && (
                      <div className="mt-4 bg-gradient-to-r from-green-900/10 to-blue-900/10 border border-green-500/20 rounded-lg p-4">
                        <h5 className="text-sm font-medium text-green-400 mb-3 flex items-center">
                          <Sparkles className="w-4 h-4 mr-2" />
                          AI Smart Scheduling Logic
                        </h5>
                        <div className="space-y-2">
                          {optimization.conflicts_avoided.map((conflict, i) => (
                            <div key={i} className="flex items-start space-x-2 text-xs text-gray-300">
                              <div className="mt-0.5 w-4 h-4 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0">
                                <CheckCircle2 className="w-3 h-3 text-green-400" />
                              </div>
                              <div>
                                <span className="text-gray-400">Detected conflict with</span> <span className="font-medium text-white">{conflict.conflict}</span>
                                <div className="text-green-400/80">↳ {conflict.resolution}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div>
                    <h4 className="text-md font-medium text-gray-300 mb-3">
                      Risk Assessment & Security Analytics
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

                      {/* Risk Trajectory Chart */}
                      {optimization.risk_trajectory && (
                        <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                          <h5 className="text-sm font-medium text-white mb-4 flex items-center">
                            <TrendingDown className="w-4 h-4 mr-2 text-blue-400" />
                            Projected Risk Reduction
                          </h5>
                          <div className="h-32 flex items-end space-x-4 px-2">
                            {optimization.risk_trajectory.map((point, i) => (
                              <div key={i} className="flex-1 flex flex-col items-center group">
                                <div className="w-full relative flex items-end justify-center h-24 bg-gray-800/50 rounded-t-lg overflow-hidden">
                                  <div 
                                    style={{ height: `${point.risk_score}%` }} 
                                    className={`w-full transition-all duration-1000 ease-out ${
                                      i === 0 ? 'bg-red-500/50' : 
                                      i === optimization.risk_trajectory.length - 1 ? 'bg-green-500/50' : 'bg-blue-500/50'
                                    }`}
                                  ></div>
                                  <span className="absolute bottom-1 text-[10px] font-bold text-white drop-shadow-md">
                                    {point.risk_score}
                                  </span>
                                </div>
                                <div className="mt-2 text-[10px] text-center text-gray-400 leading-tight">
                                  {point.label}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Resource Allocation */}
                      {optimization.detailed_resource_allocation && (
                        <div className="mt-4 bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                          <h5 className="text-sm font-medium text-white mb-3 flex items-center">
                            <Users className="w-4 h-4 mr-2 text-orange-400" />
                            Resource Allocation
                          </h5>
                          <div className="grid grid-cols-2 gap-2">
                            {optimization.detailed_resource_allocation.map((res, i) => (
                              <div key={i} className="bg-gray-800 p-2 rounded border border-gray-700 flex justify-between items-center">
                                <span className="text-xs text-gray-300">{res.role}</span>
                                <div className="flex items-center space-x-2">
                                  <span className="text-xs font-mono text-blue-400">{res.hours}h</span>
                                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                                    res.status === 'Available' ? 'bg-green-900/30 text-green-400' : 'bg-yellow-900/30 text-yellow-400'
                                  }`}>{res.status}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                        {optimization.estimated_total_downtime !== undefined && (
                          <div className="text-sm text-gray-400">
                            Estimated Total Downtime: {optimization.estimated_total_downtime}h
                          </div>
                        )}
                      </div>

                      {/* Threat Window Analysis */}
                      {optimization.threat_window_analysis && (
                        <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-red-400 mb-2 flex items-center">
                            <AlertTriangle className="w-4 h-4 mr-2" />
                            Threat Window Analysis
                          </h5>
                          <div className="space-y-2 text-xs text-gray-400">
                             <div className="flex justify-between items-center">
                               <span>Risk of Delay:</span>
                               <span className={`font-bold px-2 py-0.5 rounded ${
                                 optimization.threat_window_analysis.risk_of_delay === 'High' ? 'bg-red-900/50 text-red-400' : 
                                 optimization.threat_window_analysis.risk_of_delay === 'Medium' ? 'bg-orange-900/50 text-orange-400' : 'bg-green-900/50 text-green-400'
                               }`}>
                                 {optimization.threat_window_analysis.risk_of_delay}
                               </span>
                             </div>
                             <div className="flex justify-between items-center">
                               <span>Exploit Prob (24h):</span>
                               <span className="text-red-400 font-mono">{optimization.threat_window_analysis.exploitation_probability_next_24h}</span>
                             </div>
                             <p className="text-gray-500 italic border-t border-gray-600 pt-2 mt-2">
                               "{optimization.threat_window_analysis.description}"
                             </p>
                          </div>
                        </div>
                      )}

                      {/* Resource Impact Forecast */}
                      {optimization.resource_impact_forecast && (
                        <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-blue-400 mb-2 flex items-center">
                            <Zap className="w-4 h-4 mr-2" />
                            Resource Impact Forecast
                          </h5>
                          <div className="grid grid-cols-3 gap-2 text-center">
                            <div className="bg-gray-800 rounded p-2 border border-gray-700">
                              <div className="text-[10px] text-gray-500 uppercase">CPU Spike</div>
                              <div className="text-sm font-mono text-white">{optimization.resource_impact_forecast.cpu_spike_estimate}</div>
                            </div>
                            <div className="bg-gray-800 rounded p-2 border border-gray-700">
                              <div className="text-[10px] text-gray-500 uppercase">Memory</div>
                              <div className="text-sm font-mono text-white">{optimization.resource_impact_forecast.memory_usage_estimate}</div>
                            </div>
                            <div className="bg-gray-800 rounded p-2 border border-gray-700">
                              <div className="text-[10px] text-gray-500 uppercase">Network</div>
                              <div className="text-sm font-mono text-white">{optimization.resource_impact_forecast.network_bandwidth_impact}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Security Dependencies */}
                      {optimization.security_dependency_check && (
                        <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                          <h5 className="text-sm font-medium text-purple-400 mb-2 flex items-center">
                            <Shield className="w-4 h-4 mr-2" />
                            Security Dependencies
                          </h5>
                          <div className="text-xs text-gray-400 space-y-2">
                            <div className="flex items-center">
                              <div className={`w-2 h-2 rounded-full mr-2 ${optimization.security_dependency_check.conflicts_detected ? 'bg-red-500' : 'bg-green-500'}`}></div>
                              <span className={optimization.security_dependency_check.conflicts_detected ? 'text-red-400' : 'text-green-400'}>
                                {optimization.security_dependency_check.conflicts_detected ? "Conflicts Detected" : "No Conflicts Detected"}
                              </span>
                            </div>
                            {optimization.security_dependency_check.dependencies && (
                                <div>
                                    <span className="text-gray-500">Checked:</span> {optimization.security_dependency_check.dependencies.join(", ")}
                                </div>
                            )}
                            <p className="text-gray-500 border-t border-gray-600 pt-2 mt-2">{optimization.security_dependency_check.notes}</p>
                          </div>
                        </div>
                      )}

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
      
      {/* Company Reports Tab */}
      {activeTab === "company-reports" && (
        <div className="space-y-6">
          {loadingData && !companyReports ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            </div>
          ) : !companyReports || companyReports.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Building className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No company reports available</p>
              <button
                onClick={fetchCompanyReports}
                className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Refresh Reports
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {companyReports
                .filter(report => selectedClient === "all" || report.client_id === selectedClient)
                .map((report) => (
                <div
                  key={report.client_id}
                  className="bg-gray-800 border border-gray-700 rounded-lg p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${
                        report.risk_level === "CRITICAL" ? "bg-red-900/20 text-red-400" :
                        report.risk_level === "HIGH" ? "bg-orange-900/20 text-orange-400" :
                        report.risk_level === "MEDIUM" ? "bg-yellow-900/20 text-yellow-400" :
                        "bg-green-900/20 text-green-400"
                      }`}>
                        <Building className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{report.client_name}</h3>
                        <p className="text-sm text-gray-400">{report.tier} Tier • Last Audit: {report.last_audit}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${
                        report.compliance_score < 70 ? "text-red-400" :
                        report.compliance_score < 85 ? "text-orange-400" :
                        "text-green-400"
                      }`}>
                        {report.compliance_score}%
                      </div>
                      <div className="text-xs text-gray-500 uppercase tracking-wider">Compliance</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-gray-700/30 rounded-lg p-3">
                      <div className="text-sm text-gray-400">Total Patches</div>
                      <div className="text-xl font-semibold text-white">{report.total_patches_managed}</div>
                    </div>
                    <div className="bg-gray-700/30 rounded-lg p-3">
                      <div className="text-sm text-gray-400">Applied</div>
                      <div className="text-xl font-semibold text-green-400">{report.patches_applied}</div>
                    </div>
                    <div className="bg-gray-700/30 rounded-lg p-3">
                      <div className="text-sm text-gray-400">Pending</div>
                      <div className="text-xl font-semibold text-red-400">{report.patches_pending}</div>
                    </div>
                  </div>
                  
                  {report.top_pending_patches && report.top_pending_patches.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-2">Top Pending Patches</h4>
                      <div className="space-y-2">
                        {report.top_pending_patches.map((patch, idx) => (
                          <div key={idx} className="flex items-center justify-between bg-gray-700/50 p-2 rounded border border-gray-600">
                            <span className="text-sm text-blue-300 font-mono">{patch.cve_id}</span>
                            <span className="text-sm text-gray-400 truncate max-w-[200px]">{patch.product}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              patch.severity >= 9 ? "bg-red-900/30 text-red-400" : "bg-orange-900/30 text-orange-400"
                            }`}>
                              {patch.severity}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Remediation Tab (Incident Response) */}
      {activeTab === "remediation" && remediationContext && (
        <div className="space-y-6 animate-in fade-in duration-500">
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center">
                  <AlertTriangle className="w-6 h-6 mr-3 text-red-500" />
                  Incident Response: Active Remediation
                </h3>
                <p className="text-red-300 mt-1">
                  Target: {remediationContext.target || "Unknown System"} • Action: {remediationContext.action || "Investigation"}
                </p>
              </div>
              <div className="px-4 py-2 bg-red-900/40 rounded-lg border border-red-500/30 animate-pulse">
                <span className="text-red-400 font-mono font-bold">CRITICAL INCIDENT IN PROGRESS</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Root Cause Analysis Card */}
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
                  <Brain className="w-4 h-4 mr-2 text-purple-400" />
                  AI Root Cause Analysis
                </h4>
                <div className="space-y-3">
                  <div className="bg-gray-900/50 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-500 uppercase mb-1">Trigger Event</div>
                    <div className="text-sm text-white font-mono">Patch Deployment KB-45992</div>
                  </div>
                  <div className="bg-gray-900/50 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-500 uppercase mb-1">Impact Chain</div>
                    <div className="text-sm text-gray-300">
                      Memory Leak → Web Service Latency → <span className="text-red-400">Service Crash</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>Confidence Score:</span>
                    <span className="text-green-400 font-bold">98.5%</span>
                  </div>
                </div>
              </div>

              {/* Impact Simulation Card */}
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
                  <Activity className="w-4 h-4 mr-2 text-blue-400" />
                  Remediation Simulation
                </h4>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Projected Health Recovery</span>
                      <span className="text-green-400">99.9%</span>
                    </div>
                    <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                      <div className="bg-green-500 h-full rounded-full w-[99%]"></div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-gray-900/50 p-2 rounded text-center">
                      <div className="text-xs text-gray-500">Est. Downtime</div>
                      <div className="text-sm font-mono text-white">~45s</div>
                    </div>
                    <div className="bg-gray-900/50 p-2 rounded text-center">
                      <div className="text-xs text-gray-500">Data Loss</div>
                      <div className="text-sm font-mono text-green-400">0%</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Card */}
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 flex flex-col justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
                    <Shield className="w-4 h-4 mr-2 text-green-400" />
                    Recommended Action
                  </h4>
                  <p className="text-sm text-gray-400 mb-4">
                    AI recommends an immediate rollback of patch KB-45992 to restore service stability.
                  </p>
                </div>
                <button
                  onClick={handleSimulateRollback}
                  className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold shadow-lg shadow-red-900/20 transition-all transform hover:scale-[1.02] flex items-center justify-center"
                >
                  <RefreshCw className="w-5 h-5 mr-2" />
                  Execute Rollback Sequence
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Monitoring Tab */}
      {activeTab === "monitoring" && (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* Load simulation data when tab is opened */}
          {!monitoringData && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Activity className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No monitoring data loaded</p>
              <p className="text-sm text-gray-500 mb-6">
                Start a simulation to see live patch deployment monitoring
              </p>
              <button
                onClick={fetchMonitoringSimulation}
                disabled={loadingData || displayClients.length === 0}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center mx-auto"
              >
                {loadingData ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Activity className="w-5 h-5 mr-2" />
                    Start Monitoring Simulation
                  </>
                )}
              </button>
            </div>
          )}
          
          {monitoringData && (
            <>
              {/* Dashboard Header */}
              <div className="flex items-center justify-between bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-blue-900/20 rounded-lg">
                    <Activity className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {remediationContext ? "Live Rollback Operations" : "Live Patch Operations Center"}
                    </h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="flex h-2 w-2 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                      </span>
                      <span className="text-xs text-green-400 font-medium uppercase tracking-wider">
                        System Active • Cycle ID: #{monitoringData.cycle_id}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <button className="px-3 py-1.5 bg-red-900/20 hover:bg-red-900/40 text-red-400 border border-red-900/50 rounded text-sm font-medium transition-colors flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Emergency Stop
                  </button>
                  <button 
                    onClick={fetchMonitoringSimulation}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition-colors flex items-center"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </button>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-400 text-sm">Success Rate</span>
                  <CheckCircle className="w-4 h-4 text-green-400" />
                </div>
                <div className="text-2xl font-bold text-white">{monitoringData.metrics.success_rate}%</div>
                <div className="text-xs text-green-400 mt-1">↑ 1.2% vs last cycle</div>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-400 text-sm">Systems Patched</span>
                  <Server className="w-4 h-4 text-blue-400" />
                </div>
                <div className="text-2xl font-bold text-white">
                  {monitoringData.metrics.systems_patched} <span className="text-gray-500 text-lg font-normal">/ {monitoringData.metrics.total_systems}</span>
                </div>
                <div className="w-full bg-gray-700 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-blue-500 h-full rounded-full" style={{ width: `${monitoringData.metrics.success_rate}%` }}></div>
                </div>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-400 text-sm">Critical Failures</span>
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                </div>
                <div className="text-2xl font-bold text-white">{monitoringData.metrics.critical_failures}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {monitoringData.metrics.critical_failures > 0 ? 'AI remediation active' : '2 warnings resolved auto.'}
                </div>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-400 text-sm">Avg. Time / Server</span>
                  <Clock className="w-4 h-4 text-purple-400" />
                </div>
                <div className="text-2xl font-bold text-white">{monitoringData.metrics.avg_time_per_server}</div>
                <div className="text-xs text-green-400 mt-1">↓ 30s optimization</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Live Deployment Map */}
              <div className="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <h4 className="text-md font-semibold text-white flex items-center">
                    <Network className="w-4 h-4 mr-2 text-blue-400" />
                    Live Deployment Map
                  </h4>
                  <div className="flex items-center space-x-3 text-xs">
                    <div className="flex items-center"><div className="w-2 h-2 bg-green-500 rounded-sm mr-1"></div> Success</div>
                    <div className="flex items-center"><div className="w-2 h-2 bg-blue-500 rounded-sm mr-1 animate-pulse"></div> In Progress</div>
                    <div className="flex items-center"><div className="w-2 h-2 bg-gray-600 rounded-sm mr-1"></div> Pending</div>
                    <div className="flex items-center"><div className="w-2 h-2 bg-red-500 rounded-sm mr-1"></div> Failed</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-10 gap-2">
                  {monitoringData.nodes.map((node, i) => {
                    const statusColors = {
                      success: "bg-green-500/20 border-green-500/50 text-green-500",
                      in_progress: "bg-blue-500/20 border-blue-500/50 text-blue-400 animate-pulse",
                      pending: "bg-gray-700 border-gray-600 text-gray-500",
                      failed: "bg-red-500/20 border-red-500/50 text-red-400"
                    };
                    
                    return (
                      <div 
                        key={i} 
                        className={`aspect-square rounded border ${statusColors[node.status]} flex items-center justify-center text-[10px] font-mono transition-all hover:scale-110 cursor-pointer`}
                        title={`${node.id}: ${node.status.toUpperCase()}${node.failure_details ? ' - ' + node.failure_details.reason : ''}`}
                        onClick={() => setSelectedNode(node)}
                      >
                        {node.status === "success" && <CheckCircle className="w-3 h-3" />}
                        {node.status === "in_progress" && <Loader2 className="w-3 h-3 animate-spin" />}
                        {node.status === "failed" && <AlertTriangle className="w-3 h-3" />}
                        {node.status === "pending" && <span className="opacity-50">#{i+1}</span>}
                      </div>
                    );
                  })}
                </div>
                
                <div className="mt-6 pt-4 border-t border-gray-700">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Overall Progress</span>
                    <span className="text-white font-mono">{monitoringData.metrics.success_rate}%</span>
                  </div>
                  <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-blue-500 to-green-400 h-full rounded-full transition-all duration-1000" style={{ width: `${monitoringData.metrics.success_rate}%` }}></div>
                  </div>
                </div>
              </div>

              {/* Real-time Log Stream */}
              <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden flex flex-col h-[400px]">
                <div className="bg-gray-800 px-4 py-3 border-b border-gray-700 flex justify-between items-center">
                  <span className="text-xs font-mono text-gray-400 flex items-center">
                    <Terminal className="w-3 h-3 mr-2" />
                    patch_deploy.log
                  </span>
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                </div>
                <div className="flex-1 p-4 font-mono text-xs overflow-y-auto space-y-2">
                  {monitoringData.logs.map((log, i) => (
                    <div key={i} className="flex space-x-2 opacity-80 hover:opacity-100 transition-opacity">
                      <span className="text-gray-500 shrink-0">[{log.time}]</span>
                      <span className={`shrink-0 font-bold ${
                        log.level === "INFO" ? "text-blue-400" :
                        log.level === "SUCCESS" ? "text-green-400" :
                        log.level === "WARN" ? "text-yellow-400" : "text-red-400"
                      }`}>{log.level}</span>
                      <span className="text-gray-300">{log.msg}</span>
                    </div>
                  ))}
                  <div className="flex items-center space-x-2 animate-pulse text-blue-400 mt-2">
                    <span>➜</span>
                    <span className="w-2 h-4 bg-blue-400"></span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Selected Node Details Modal */}
            {selectedNode && selectedNode.failure_details && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedNode(null)}>
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white flex items-center">
                      <AlertTriangle className="w-5 h-5 mr-2 text-red-400" />
                      Failure Analysis: {selectedNode.id}
                    </h3>
                    <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-white">
                      ×
                    </button>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                      <div className="text-sm font-medium text-red-400 mb-2">Error Details</div>
                      <div className="text-sm text-gray-300">{selectedNode.failure_details.reason}</div>
                      <div className="text-xs text-gray-500 mt-2">Error Code: {selectedNode.failure_details.error_code}</div>
                      <div className="text-xs text-gray-500">Timestamp: {new Date(selectedNode.failure_details.timestamp).toLocaleString()}</div>
                    </div>
                    
                    <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                      <div className="text-sm font-medium text-blue-400 mb-2 flex items-center">
                        <Brain className="w-4 h-4 mr-2" />
                        AI Remediation Analysis
                      </div>
                      <div className="text-sm text-gray-300 mb-3">{selectedNode.failure_details.ai_remediation.analysis}</div>
                      <div className="flex items-center justify-between bg-gray-900/50 rounded p-2">
                        <span className="text-xs text-gray-400">Confidence Score:</span>
                        <span className="text-sm font-mono text-green-400">{(selectedNode.failure_details.ai_remediation.confidence_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    
                    <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                      <div className="text-sm font-medium text-green-400 mb-2">Suggested Action</div>
                      <div className="text-sm text-gray-300">{selectedNode.failure_details.ai_remediation.suggested_action}</div>
                      {selectedNode.failure_details.ai_remediation.automated_fix_available && (
                        <button className="mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors flex items-center">
                          <Zap className="w-4 h-4 mr-2" />
                          Apply Automated Fix
                        </button>
                      )}
                    </div>
                    
                    <div className="bg-gray-700/30 rounded-lg p-3">
                      <div className="text-xs text-gray-400 mb-2">Server Information</div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div><span className="text-gray-500">Region:</span> <span className="text-white">{selectedNode.region}</span></div>
                        <div><span className="text-gray-500">IP:</span> <span className="text-white font-mono">{selectedNode.ip}</span></div>
                        <div><span className="text-gray-500">Progress:</span> <span className="text-white">{selectedNode.patch_progress}%</span></div>
                        <div><span className="text-gray-500">Status:</span> <span className="text-red-400">{selectedNode.status}</span></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
          )}

          {/* Bottom Section: Timeline */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h4 className="text-md font-semibold text-white mb-4 flex items-center">
              <Clock className="w-4 h-4 mr-2 text-purple-400" />
              Deployment Timeline
            </h4>
            <div className="relative pt-6 pb-2">
              <div className="absolute top-0 left-0 w-full h-1 bg-gray-700 mt-8"></div>
              <div className="grid grid-cols-5 gap-4 relative z-10">
                {[
                  { stage: "Pre-Flight", status: "complete", time: "23:15" },
                  { stage: "Distribution", status: "complete", time: "23:20" },
                  { stage: "Installation", status: "active", time: "Now" },
                  { stage: "Verification", status: "pending", time: "Est. 23:45" },
                  { stage: "Reporting", status: "pending", time: "Est. 23:50" },
                ].map((step, i) => (
                  <div key={i} className="text-center">
                    <div className={`w-4 h-4 mx-auto rounded-full border-2 mb-2 ${
                      step.status === "complete" ? "bg-green-500 border-green-500" :
                      step.status === "active" ? "bg-blue-500 border-blue-500 animate-pulse" :
                      "bg-gray-800 border-gray-600"
                    }`}></div>
                    <div className={`text-sm font-medium ${
                      step.status === "active" ? "text-blue-400" : "text-gray-300"
                    }`}>{step.stage}</div>
                    <div className="text-xs text-gray-500 mt-1">{step.time}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Success Overlay */}
      {showSuccess && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100] animate-in fade-in duration-300">
          <div className="bg-gray-800 border border-green-500/50 rounded-xl p-8 max-w-md w-full text-center shadow-2xl shadow-green-900/50 transform animate-in zoom-in-95 duration-300">
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-10 h-10 text-green-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Remediation Complete</h3>
            <p className="text-gray-300 mb-6">
              Patch KB-45992 has been successfully rolled back. System stability has been restored to 99.9%.
            </p>
            <div className="bg-gray-900/50 rounded-lg p-4 mb-6 border border-gray-700">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Services Restored</span>
                <span className="text-green-400">3/3</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Mean Time to Recover</span>
                <span className="text-blue-400">45s</span>
              </div>
            </div>
            <button
              onClick={() => {
                setShowSuccess(false);
                setActiveTab("cve-analysis");
                // Optional: Clear remediation context here if we had a callback
              }}
              className="w-full py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-bold transition-colors"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedPatchManagement;
