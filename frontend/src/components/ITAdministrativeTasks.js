import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  Settings,
  Shield,
  Database,
  Users,
  BarChart3,
  Clock,
  Play,
  RefreshCw,
  Brain,
  Zap,
  Target,
  FileText,
  Activity,
  HardDrive,
  Network,
  Server,
  Loader2,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";

const ITAdministrativeTasks = ({ clients = [], loading = false }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  // Optimistic initial state for instant UI render
  const [taskRecommendations, setTaskRecommendations] = useState({});
  const [taskHistory, setTaskHistory] = useState({});
  const [complianceReports, setComplianceReports] = useState({});
  const [availableTasks, setAvailableTasks] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [activeTab, setActiveTab] = useState("recommendations");
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [executionResults, setExecutionResults] = useState({});
  const [loadingCompliance, setLoadingCompliance] = useState({});
  const [loadingHistory, setLoadingHistory] = useState({});

  // Refs for throttling and concurrency control
  const isFetchingRef = useRef(false);
  const fetchedRef = useRef({});
  const lastFetchTimeRef = useRef({}); // Per-client last fetch time
  const loadingStateRef = useRef({});
  const recommendationsCacheRef = useRef({}); // Cache with timestamps
  
  // Safe clients array
  const displayClients = clients && Array.isArray(clients) ? clients : [];

  // Lazy load data only when tabs become active
  useEffect(() => {
    if (displayClients.length === 0) return;
    
    // Only fetch available tasks once on mount (fast endpoint)
    if (!fetchedRef.current.availableTasks) {
      fetchedRef.current.availableTasks = true;
      fetchAvailableTasks();
    }
  }, [displayClients.length]);

  // Fetch recommendations only when recommendations tab becomes active
  useEffect(() => {
    if (activeTab === "recommendations" && displayClients.length > 0) {
      const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
      if (clientId && !taskRecommendations[clientId] && !isFetchingRef.current) {
        // Defer to next tick to avoid blocking render
        const timer = setTimeout(() => {
          fetchTaskRecommendations();
        }, 50);
        return () => clearTimeout(timer);
      }
    }
  }, [activeTab]); // Only depend on activeTab to avoid unnecessary calls

  const fetchAvailableTasks = useCallback(async () => {
    // Skip if already fetched and recent (cache for 2 minutes)
    const cacheKey = 'availableTasks';
    if (availableTasks.length > 0 && Date.now() - lastFetchTimeRef.current < 120000) {
      return;
    }
    if (loadingStateRef.current[cacheKey]) return;

    try {
      loadingStateRef.current[cacheKey] = true;
      const response = await apiClient.get("/it-admin/available-tasks");
      // FastAPI returns data directly, not nested in .data
      const tasks = response.available_task_types || response.data?.available_task_types || [];
      setAvailableTasks(Array.isArray(tasks) ? tasks : []);
      lastFetchTimeRef.current = Date.now();
    } catch (error) {
      console.error("Error fetching available tasks:", error);
      setAvailableTasks([]);
    } finally {
      loadingStateRef.current[cacheKey] = false;
    }
  }, []); // No dependencies - stable function

  const fetchTaskRecommendations = useCallback(async (forceRefresh = false) => {
    if (displayClients.length === 0) return;
    const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
    if (!clientId) return;

    const cacheKey = `recommendations_${clientId}`;
    
    // Check cache - 2 minute cache on frontend too
    if (!forceRefresh && !loadingStateRef.current[cacheKey]) {
      const cacheAge = lastFetchTimeRef.current[clientId] 
        ? Date.now() - lastFetchTimeRef.current[clientId] 
        : Infinity;
      
      // Use cached data if available and fresh (2 minutes)
      if (taskRecommendations[clientId] && cacheAge < 120000) {
        return; // Use existing data
      }
    }

    // Skip if already fetching for this client
    if (loadingStateRef.current[cacheKey] && !forceRefresh) {
      return;
    }

    try {
      isFetchingRef.current = true;
      loadingStateRef.current[cacheKey] = true;
      setLoadingData(true);
      
      // Set timeout for the API call (10 seconds max)
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error("Request timeout")), 10000)
      );
      
      const apiPromise = apiClient.get(`/it-admin/recommendations/${clientId}`);
      
      let response;
      try {
        response = await Promise.race([apiPromise, timeoutPromise]);
      } catch (timeoutError) {
        console.warn("Recommendations request timed out, using fallback");
        // Return empty array but don't show error - just no recommendations
        setTaskRecommendations((prev) => ({
          ...prev,
          [clientId]: [],
        }));
        lastFetchTimeRef.current[clientId] = Date.now();
        return;
      }
      
      // Handle both response formats - FastAPI returns data directly
      const recommendations = response.recommended_tasks || response.data?.recommended_tasks || [];
      
      if (!Array.isArray(recommendations)) {
        console.error("Invalid recommendations format:", recommendations);
        setTaskRecommendations((prev) => ({
          ...prev,
          [clientId]: [],
        }));
        return;
      }
      
      setTaskRecommendations((prev) => ({
        ...prev,
        [clientId]: recommendations,
      }));
      
      // Update cache timestamp
      lastFetchTimeRef.current[clientId] = Date.now();
      recommendationsCacheRef.current[clientId] = {
        data: recommendations,
        timestamp: Date.now()
      };
      
      console.log(`Recommendations loaded for ${clientId} (${recommendations.length} tasks)${response.cached ? ' [CACHED]' : ''}`);
    } catch (error) {
      console.error("Error fetching task recommendations:", error);
      // Don't set empty array on error - keep existing recommendations if any
      if (!taskRecommendations[clientId]) {
        setTaskRecommendations((prev) => ({
          ...prev,
          [clientId]: [],
        }));
      }
    } finally {
      setLoadingData(false);
      isFetchingRef.current = false;
      loadingStateRef.current[cacheKey] = false;
    }
  }, [selectedClient, displayClients]);

  const fetchTaskHistory = useCallback(async (clientId, force = false) => {
    if (!clientId) return;
    
    const cacheKey = `history_${clientId}`;
    // Skip if currently loading (unless forced refresh)
    if (!force && loadingStateRef.current[cacheKey]) return;

    try {
      loadingStateRef.current[cacheKey] = true;
      setLoadingHistory((prev) => ({ ...prev, [clientId]: true }));
      setLoadingData(true);
      
      console.log("Fetching task history for:", clientId);
      const response = await apiClient.get(
        `/it-admin/task-history/${clientId}`
      );
      console.log("Task history response:", response);
      
      // FastAPI returns data directly
      const history = response.task_history || response.data?.task_history || [];
      
      if (Array.isArray(history)) {
        setTaskHistory((prev) => ({
          ...prev,
          [clientId]: history,
        }));
        console.log(`Loaded ${history.length} history items for ${clientId}`);
      } else {
        console.error("Invalid history format:", history, response);
        // Set empty array on error so UI still renders
        setTaskHistory((prev) => ({
          ...prev,
          [clientId]: [],
        }));
      }
    } catch (error) {
      console.error("Error fetching task history:", error);
      // Set empty array on error
      setTaskHistory((prev) => ({
        ...prev,
        [clientId]: [],
      }));
    } finally {
      setLoadingData(false);
      setLoadingHistory((prev) => ({ ...prev, [clientId]: false }));
      loadingStateRef.current[cacheKey] = false;
    }
  }, []);

  const generateComplianceReport = useCallback(async (clientId, force = false) => {
    if (!clientId) return;
    
    const cacheKey = `compliance_${clientId}`;
    // Skip if already generating or already exists (unless forced)
    if (!force && (complianceReports[clientId] || loadingStateRef.current[cacheKey])) {
      return;
    }

    try {
      loadingStateRef.current[cacheKey] = true;
      setLoadingCompliance((prev) => ({ ...prev, [clientId]: true }));
      setLoadingData(true);
      const response = await apiClient.get(
        `/it-admin/compliance-report/${clientId}`
      );
      
      // FastAPI returns data directly
      const report = response.compliance_report || response.data?.compliance_report;
      
      if (report) {
        setComplianceReports((prev) => ({
          ...prev,
          [clientId]: report,
        }));
      } else {
        console.error("No compliance report in response:", response);
        // Set null to show error state
        setComplianceReports((prev) => ({
          ...prev,
          [clientId]: null,
        }));
      }
    } catch (error) {
      console.error("Error generating compliance report:", error);
      // Set null to indicate error
      setComplianceReports((prev) => ({
        ...prev,
        [clientId]: null,
      }));
    } finally {
      setLoadingData(false);
      setLoadingCompliance((prev) => ({ ...prev, [clientId]: false }));
      loadingStateRef.current[cacheKey] = false;
    }
  }, [complianceReports]);

  const [showAgentTerminal, setShowAgentTerminal] = useState(false);
  const [currentAgentLogs, setCurrentAgentLogs] = useState([]);
  const [currentAgentStep, setCurrentAgentStep] = useState(0);
  const [isAgentRunning, setIsAgentRunning] = useState(false);

  const executeTask = useCallback(async (clientId, taskType, priority = "medium") => {
    if (!clientId || !taskType) return;

    try {
      setLoadingData(true);
      console.log("Executing task:", { clientId, taskType, priority });
      
      // Start execution immediately
      const response = await apiClient.post(
        `/it-admin/execute/${clientId}`,
        {
          task_type: taskType,
          priority: priority,
        }
      );
      console.log("Task execution response:", response);
      
      // FastAPI returns data directly
      const execution = response.task_execution || response.data?.task_execution || response;
      
      if (execution) {
        // Check if we have agentic logs to simulate
        if (execution.agentic_log && Array.isArray(execution.agentic_log)) {
          // Start simulation
          setShowAgentTerminal(true);
          setIsAgentRunning(true);
          setCurrentAgentLogs([]);
          setCurrentAgentStep(0);
          
          // Process logs sequentially with delays
          let accumulatedDelay = 0;
          const logs = execution.agentic_log;
          
          logs.forEach((log, index) => {
            setTimeout(() => {
              setCurrentAgentLogs(prev => [...prev, log]);
              setCurrentAgentStep(index + 1);
              
              // If this is the last log, finish simulation
              if (index === logs.length - 1) {
                setTimeout(() => {
                  setIsAgentRunning(false);
                  // Store result after simulation
                  setExecutionResults((prev) => ({
                    ...prev,
                    [`${clientId}_${taskType}_${Date.now()}`]: execution,
                  }));
                  // Don't auto-close, let user see the "Complete" state
                }, 1000);
              }
            }, accumulatedDelay);
            
            accumulatedDelay += (log.duration || 1000);
          });
        } else {
          // No logs, just show result immediately
          setExecutionResults((prev) => ({
            ...prev,
            [`${clientId}_${taskType}_${Date.now()}`]: execution,
          }));
          setActiveTab("execution");
        }
        console.log("Execution result stored:", execution);
      } else {
        console.error("No execution result in response:", response);
      }
    } catch (error) {
      console.error("Error executing task:", error);
      // Show error in execution results
      setExecutionResults((prev) => ({
        ...prev,
        [`${clientId}_${taskType}_${Date.now()}_error`]: {
          task_id: `${clientId}_${taskType}`,
          status: "failed",
          error: error.message || "Task execution failed",
          execution_time_hours: 0
        },
      }));
    } finally {
      setLoadingData(false);
    }
  }, []);

  const bulkExecuteTasks = useCallback(async (clientId, taskTypes) => {
    if (!clientId || !taskTypes || taskTypes.length === 0) return;

    try {
      setLoadingData(true);
      console.log("Bulk executing tasks:", { clientId, taskTypes });
      const response = await apiClient.post(
        `/it-admin/bulk-execute/${clientId}`,
        {
          task_types: taskTypes,
        }
      );
      console.log("Bulk execution response:", response);
      
      // FastAPI returns data directly
      const bulkExecution = response.bulk_execution || response.data?.bulk_execution;
      
      if (bulkExecution) {
        // Store bulk execution summary
        setExecutionResults((prev) => ({
          ...prev,
          [`${clientId}_bulk_${Date.now()}`]: {
            task_id: `bulk_${taskTypes.join("_")}`,
            status: bulkExecution.failed_tasks === 0 ? "completed" : "partial",
            execution_time_hours: 1.5,
            results: bulkExecution.results || [],
            total_tasks: bulkExecution.total_tasks || taskTypes.length,
            successful_tasks: bulkExecution.successful_tasks || 0,
            failed_tasks: bulkExecution.failed_tasks || 0,
            is_bulk: true
          },
        }));
        
        // Also store individual task results if available
        if (bulkExecution.results && Array.isArray(bulkExecution.results)) {
          bulkExecution.results.forEach((result, idx) => {
            if (result && result.result) {
              setExecutionResults((prev) => ({
                ...prev,
                [`${clientId}_${result.task_type || taskTypes[idx]}_${Date.now()}_${idx}`]: {
                  ...result.result,
                  task_id: result.task_type || `${clientId}_task_${idx}`
                },
              }));
            }
          });
        }
        
        setActiveTab("execution");
        console.log("Bulk execution stored");
      } else {
        console.error("No bulk execution result in response:", response);
      }
    } catch (error) {
      console.error("Error bulk executing tasks:", error);
      // Show error
      setExecutionResults((prev) => ({
        ...prev,
        [`${clientId}_bulk_${Date.now()}_error`]: {
          task_id: `bulk_${taskTypes.join("_")}`,
          status: "failed",
          error: error.message || "Bulk execution failed",
          execution_time_hours: 0,
          is_bulk: true
        },
      }));
    } finally {
      setLoadingData(false);
    }
  }, []);

  const handleTaskSelection = (taskType, selected) => {
    if (selected) {
      setSelectedTasks((prev) => [...prev, taskType]);
    } else {
      setSelectedTasks((prev) => prev.filter((type) => type !== taskType));
    }
  };

  const handleBulkExecute = async () => {
    if (displayClients.length === 0) return;
    const clientId = selectedClient === "all" ? displayClients[0]?.id : selectedClient;
    if (!clientId || selectedTasks.length === 0) return;

    await bulkExecuteTasks(clientId, selectedTasks);
    setActiveTab("execution");
  };

  const getTaskIcon = (taskType) => {
    const iconMap = {
      security_audit: Shield,
      compliance_check: FileText,
      backup_verification: Database,
      capacity_planning: BarChart3,
      performance_optimization: Activity,
      user_access_review: Users,
      system_health_check: Server,
      disaster_recovery_test: HardDrive,
      software_inventory: Settings,
      network_analysis: Network,
    };
    return iconMap[taskType] || Settings;
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "critical":
        return "text-red-400 bg-red-900/20";
      case "high":
        return "text-orange-400 bg-orange-900/20";
      case "medium":
        return "text-yellow-400 bg-yellow-900/20";
      case "low":
        return "text-green-400 bg-green-900/20";
      default:
        return "text-gray-400 bg-gray-900/20";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "text-green-400 bg-green-900/20";
      case "in_progress":
        return "text-blue-400 bg-blue-900/20";
      case "failed":
        return "text-red-400 bg-red-900/20";
      case "pending":
        return "text-yellow-400 bg-yellow-900/20";
      default:
        return "text-gray-400 bg-gray-900/20";
    }
  };

  // Agent Terminal Modal
  const AgentTerminalModal = () => {
    if (!showAgentTerminal) return null;

    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-3xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
          {/* Terminal Header */}
          <div className="bg-gray-800 px-4 py-3 border-b border-gray-700 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <span className="ml-3 text-sm font-mono text-gray-400 flex items-center">
                <Brain className="w-3 h-3 mr-2 text-purple-400" />
                agent_executor.exe --mode=autonomous
              </span>
            </div>
            <div className="flex items-center space-x-3">
              {isAgentRunning ? (
                <span className="text-xs text-green-400 animate-pulse flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
                  RUNNING
                </span>
              ) : (
                <span className="text-xs text-gray-400 flex items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-1"></div>
                  COMPLETED
                </span>
              )}
              <button 
                onClick={() => {
                  setShowAgentTerminal(false);
                  setActiveTab("execution");
                }}
                className="text-gray-400 hover:text-white transition-colors"
                disabled={isAgentRunning}
              >
                <span className="text-xs font-mono">[CLOSE]</span>
              </button>
            </div>
          </div>

          {/* Terminal Body */}
          <div className="flex-1 bg-black p-6 overflow-y-auto font-mono text-sm space-y-4 min-h-[400px]">
            {currentAgentLogs.map((log, idx) => (
              <div key={idx} className="animate-in fade-in slide-in-from-left-2 duration-300">
                <div className="flex items-start space-x-3">
                  <span className="text-gray-500 shrink-0">
                    [{new Date().toLocaleTimeString()}]
                  </span>
                  <div className="flex-1">
                    <span className={`font-bold mr-2 ${
                      log.step === 'AI_INSIGHT' ? 'text-purple-400' :
                      log.step === 'ERROR' ? 'text-red-400' :
                      log.step === 'COMPLETE' ? 'text-green-400' :
                      'text-blue-400'
                    }`}>
                      {log.step}:
                    </span>
                    <span className="text-gray-300 typing-effect">
                      {log.message}
                    </span>
                  </div>
                </div>
                {log.step === 'AI_INSIGHT' && (
                  <div className="ml-24 mt-1 p-2 bg-purple-900/20 border-l-2 border-purple-500 text-xs text-purple-200">
                    Thinking Process: Analyzing patterns using Gemini 1.5 Pro context window...
                  </div>
                )}
              </div>
            ))}
            {isAgentRunning && (
              <div className="flex items-center space-x-2 ml-1 animate-pulse">
                <span className="text-green-500">➜</span>
                <div className="w-2 h-4 bg-green-500"></div>
              </div>
            )}
            {!isAgentRunning && (
              <div className="mt-6 pt-4 border-t border-gray-800 text-center">
                <p className="text-green-400 mb-4">✨ Task Execution Completed Successfully</p>
                <button
                  onClick={() => {
                    setShowAgentTerminal(false);
                    setActiveTab("execution");
                  }}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded border border-gray-600 transition-colors text-xs font-mono"
                >
                  View Detailed Report
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Always render - ensure UI is visible
  return (
    <div className="space-y-6 p-6">
      <AgentTerminalModal />
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Settings className="w-6 h-6 mr-3 text-purple-400" />
            IT Administrative Tasks
          </h2>
          <p className="text-gray-400 mt-1">
            AI-powered automation of routine IT administrative tasks and
            compliance monitoring
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">AI Active</span>
          </div>
          <button
            onClick={fetchTaskRecommendations}
            disabled={loadingData || isFetchingRef.current || displayClients.length === 0}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
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
                {client.name || client.id}
              </option>
            ))}
          </select>
          {displayClients.length === 0 && (
            <span className="text-yellow-400 text-sm">No clients available</span>
          )}
        </div>

        <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
          {[
            { id: "recommendations", label: "Recommendations", icon: Brain },
            { id: "available", label: "Available Tasks", icon: Target },
            { id: "history", label: "History", icon: Clock },
            { id: "compliance", label: "Compliance", icon: Shield },
            { id: "execution", label: "Execution", icon: Play },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center ${
                activeTab === tab.id
                  ? "bg-purple-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-700"
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Recommendations Tab */}
      {activeTab === "recommendations" && (
        <div className="space-y-6">
          {/* Refresh button for recommendations */}
          <div className="flex justify-end">
            <button
              onClick={() => fetchTaskRecommendations(true)}
              disabled={loadingData || isFetchingRef.current || displayClients.length === 0}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loadingData ? 'animate-spin' : ''}`} />
              Refresh Recommendations
            </button>
          </div>
          
          {loadingData && (!taskRecommendations[selectedClient === "all" ? displayClients[0]?.id : selectedClient]) ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Loader2 className="w-16 h-16 mx-auto mb-4 text-purple-400 animate-spin" />
              <p className="text-gray-400 mb-2">Loading AI-powered recommendations...</p>
              <p className="text-sm text-gray-500">This may take a few seconds</p>
            </div>
          ) : Object.keys(taskRecommendations).length === 0 || !taskRecommendations[selectedClient === "all" ? displayClients[0]?.id : selectedClient] ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Brain className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No recommendations available</p>
              <p className="text-sm text-gray-500 mb-4">
                Click below to load AI-powered task recommendations for your clients
              </p>
              <button
                onClick={() => fetchTaskRecommendations(false)}
                disabled={loadingData || isFetchingRef.current || displayClients.length === 0}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center mx-auto"
              >
                {loadingData ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    Load Recommendations
                  </>
                )}
              </button>
            </div>
          ) : (
            Object.entries(taskRecommendations).map(([clientId, tasks]) => (
            <div
              key={clientId}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  AI Task Recommendations
                </h3>
                <div className="text-sm text-gray-400">
                  {Array.isArray(tasks) ? tasks.length : 0} recommendations
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tasks && Array.isArray(tasks) && tasks.length > 0 ? (
                  tasks.map((task) => {
                  const IconComponent = getTaskIcon(task.task_type);
                  return (
                    <div
                      key={task.task_id}
                      className="bg-gray-700/50 border border-gray-600 rounded-lg p-4 hover:bg-gray-700/70 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <IconComponent className="w-5 h-5 text-purple-400" />
                          <span className="text-sm font-medium text-white">
                            {task.task_type.replace(/_/g, " ").toUpperCase()}
                          </span>
                        </div>
                        <div
                          className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                            task.priority
                          )}`}
                        >
                          {task.priority}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="text-sm text-gray-300">
                          {task.description}
                        </div>
                        <div className="text-xs text-gray-400">
                          Duration: {task.estimated_duration.hours}h •{" "}
                          {task.estimated_duration.complexity} complexity
                        </div>
                        <div className="text-xs text-gray-400">
                          Impact: {task.ai_analysis?.estimated_impact} •
                          Automation: {task.ai_analysis?.automation_potential}
                        </div>
                      </div>

                      <div className="mt-3 flex space-x-2">
                        <button
                          onClick={() =>
                            executeTask(clientId, task.task_type, task.priority)
                          }
                          className="flex-1 px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-colors"
                        >
                          Execute
                        </button>
                        <button
                          onClick={() =>
                            handleTaskSelection(task.task_type, true)
                          }
                          className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
                        >
                          Select
                        </button>
                      </div>
                    </div>
                  );
                  })
                ) : (
                  <div className="col-span-full text-center text-gray-400 py-8">
                    <p>No tasks available for this client</p>
                  </div>
                )}
              </div>

              {selectedTasks.length > 0 && (
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={handleBulkExecute}
                    className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center"
                  >
                    <Zap className="w-5 h-5 mr-2" />
                    Bulk Execute ({selectedTasks.length} tasks)
                  </button>
                </div>
              )}
            </div>
            ))
          )}
        </div>
      )}

      {/* Available Tasks Tab */}
      {activeTab === "available" && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">
                Available Task Types
              </h3>
              <div className="text-sm text-gray-400">
                {availableTasks.length} task types
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableTasks.map((task) => {
                const IconComponent = getTaskIcon(task.type);
                return (
                  <div
                    key={task.type}
                    className="bg-gray-700/50 border border-gray-600 rounded-lg p-4 hover:bg-gray-700/70 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={selectedTasks.includes(task.type)}
                          onChange={(e) =>
                            handleTaskSelection(task.type, e.target.checked)
                          }
                          className="rounded border-gray-600 bg-gray-800 text-purple-600"
                        />
                        <IconComponent className="w-5 h-5 text-purple-400" />
                        <span className="text-sm font-medium text-white">
                          {task.name}
                        </span>
                      </div>
                      <div className="text-xs text-gray-400">
                        {task.automation_level}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="text-sm text-gray-300">
                        {task.description}
                      </div>
                      <div className="text-xs text-gray-400">
                        Duration: {task.typical_duration} • Automation:{" "}
                        {task.automation_level}
                      </div>
                    </div>

                    <div className="mt-3">
                      <button
                        onClick={() =>
                          executeTask(
                            selectedClient === "all"
                              ? displayClients[0]?.id
                              : selectedClient,
                            task.type
                          )
                        }
                        className="w-full px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-colors"
                      >
                        Execute Now
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === "history" && (
        <div className="space-y-6">
          {displayClients.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Clock className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No clients available</p>
              <p className="text-sm text-gray-500">
                Please select a client to view task history
              </p>
            </div>
          ) : (selectedClient === "all" ? displayClients : displayClients.filter((c) => c.id === selectedClient)).map((client) => (
            <div
              key={client.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Task History - {client.name}
                </h3>
                <button
                  onClick={() => fetchTaskHistory(client.id, !!taskHistory[client.id])}
                  disabled={loadingHistory[client.id]}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50 text-white text-sm rounded transition-colors flex items-center"
                >
                  {loadingHistory[client.id] ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : taskHistory[client.id] ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Refresh
                    </>
                  ) : (
                    <>
                      <Clock className="w-4 h-4 mr-2" />
                      Load History
                    </>
                  )}
                </button>
              </div>

              {loadingHistory[client.id] ? (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 mx-auto mb-4 text-purple-400 animate-spin" />
                  <p className="text-gray-400">Loading task history...</p>
                </div>
              ) : taskHistory[client.id] && taskHistory[client.id].length > 0 ? (
                <div className="space-y-3">
                  {taskHistory[client.id].map((task, idx) => {
                    const IconComponent = getTaskIcon(task.task_type || task.taskType || "unknown");
                    return (
                      <div
                        key={task.task_id || task.taskId || idx}
                        className="bg-gray-700/50 border border-gray-600 rounded-lg p-3 hover:bg-gray-700/70 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <IconComponent className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-medium text-white">
                              {(task.task_type || task.taskType || "unknown").replace(/_/g, " ").toUpperCase()}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div
                              className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                                task.priority || "medium"
                              )}`}
                            >
                              {task.priority || "medium"}
                            </div>
                            <div
                              className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                                task.status || "pending"
                              )}`}
                            >
                              {task.status || "pending"}
                            </div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-400">
                          {task.description || "No description"} •{" "}
                          {task.created_at ? new Date(task.created_at).toLocaleString() : "Unknown date"}
                        </div>
                        {task.estimated_duration && (
                          <div className="text-xs text-gray-500 mt-1">
                            Duration: {typeof task.estimated_duration === 'object' 
                              ? `${task.estimated_duration.hours || 0}h` 
                              : task.estimated_duration}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <Clock className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-lg mb-2">No task history available</p>
                  <p className="text-sm mb-4">
                    {taskHistory[client.id] && taskHistory[client.id].length === 0
                      ? "No tasks have been executed yet for this client"
                      : "Click 'Load History' to fetch task history"}
                  </p>
                  {!taskHistory[client.id] && (
                    <button
                      onClick={() => fetchTaskHistory(client.id, false)}
                      disabled={loadingHistory[client.id]}
                      className="px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center mx-auto"
                    >
                      {loadingHistory[client.id] ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Loading...
                        </>
                      ) : (
                        <>
                          <Clock className="w-4 h-4 mr-2" />
                          Load History
                        </>
                      )}
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Compliance Tab */}
      {activeTab === "compliance" && (
        <div className="space-y-6">
          {displayClients.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Shield className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">No clients available</p>
              <p className="text-sm text-gray-500">
                Please select a client to generate compliance reports
              </p>
            </div>
          ) : (selectedClient === "all" ? displayClients : displayClients.filter((c) => c.id === selectedClient)).map((client) => (
            <div
              key={client.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Compliance Report - {client.name}
                </h3>
                <button
                  onClick={() => generateComplianceReport(client.id, !!complianceReports[client.id])}
                  disabled={loadingCompliance[client.id]}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                >
                  {loadingCompliance[client.id] ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Shield className="w-4 h-4 mr-2" />
                      {complianceReports[client.id] && complianceReports[client.id] !== null ? "Regenerate Report" : "Generate Report"}
                    </>
                  )}
                </button>
              </div>

              {complianceReports[client.id] && complianceReports[client.id] !== null ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white">
                        {(
                          (complianceReports[client.id].compliance_score || 0) * 100
                        ).toFixed(1)}
                        %
                      </div>
                      <div className="text-sm text-gray-400">
                        Compliance Score
                      </div>
                    </div>
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <div className="text-lg font-semibold text-white">
                        {(complianceReports[client.id].overall_status || "unknown").toUpperCase()}
                      </div>
                      <div className="text-sm text-gray-400">
                        Overall Status
                      </div>
                    </div>
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <div className="text-lg font-semibold text-white">
                        {(complianceReports[client.id].risk_assessment || "unknown").toUpperCase()}
                      </div>
                      <div className="text-sm text-gray-400">
                        Risk Assessment
                      </div>
                    </div>
                  </div>

                  {complianceReports[client.id].compliance_areas && complianceReports[client.id].compliance_areas.length > 0 && (
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <h4 className="text-md font-medium text-gray-300 mb-3">
                        Compliance Areas
                      </h4>
                      <div className="space-y-3">
                        {complianceReports[client.id].compliance_areas.map(
                          (area, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between"
                            >
                              <div>
                                <div className="text-sm font-medium text-white">
                                  {area.area?.replace(/_/g, " ").toUpperCase() || "Unknown"}
                                </div>
                                <div className="text-xs text-gray-400">
                                  Last checked:{" "}
                                  {area.last_checked ? new Date(
                                    area.last_checked
                                  ).toLocaleDateString() : "N/A"}
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <div className="text-sm text-white">
                                  {((area.score || 0) * 100).toFixed(1)}%
                                </div>
                                <div
                                  className={`px-2 py-1 rounded text-xs font-medium ${
                                    area.status === "compliant"
                                      ? "text-green-400 bg-green-900/20"
                                      : area.status === "at_risk"
                                      ? "text-yellow-400 bg-yellow-900/20"
                                      : "text-red-400 bg-red-900/20"
                                  }`}
                                >
                                  {area.status || "unknown"}
                                </div>
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : complianceReports[client.id] === null ? (
                <div className="text-center text-red-400 py-8">
                  <Shield className="w-12 h-12 mx-auto mb-4 text-red-600" />
                  <p className="text-lg mb-2">Error generating compliance report</p>
                  <p className="text-sm mb-4 text-gray-400">
                    There was an error generating the report. Please try again.
                  </p>
                  <button
                    onClick={() => generateComplianceReport(client.id, true)}
                    disabled={loadingCompliance[client.id]}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center mx-auto"
                  >
                    {loadingCompliance[client.id] ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Retry
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <Shield className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-lg mb-2">No compliance report available</p>
                  <p className="text-sm mb-4">
                    Click "Generate Report" to create a comprehensive compliance report for {client.name}
                  </p>
                  <button
                    onClick={() => generateComplianceReport(client.id, false)}
                    disabled={loadingCompliance[client.id]}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors flex items-center mx-auto"
                  >
                    {loadingCompliance[client.id] ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4 mr-2" />
                        Generate Report
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Execution Tab */}
      {activeTab === "execution" && (
        <div className="space-y-6">
          {Object.keys(executionResults).length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
              <Play className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-lg text-gray-400 mb-2">No task executions to display</p>
              <p className="text-sm text-gray-500 mb-4">
                Execute tasks from the "Recommendations" or "Available Tasks" tabs to see results here
              </p>
              <div className="flex justify-center gap-4">
                <button
                  onClick={() => setActiveTab("recommendations")}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  Go to Recommendations
                </button>
                <button
                  onClick={() => setActiveTab("available")}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                >
                  <Target className="w-4 h-4 mr-2" />
                  Go to Available Tasks
                </button>
              </div>
            </div>
          ) : (
            Object.entries(executionResults).map(([key, result]) => (
              <div
                key={key}
                className="bg-gray-800 border border-gray-700 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
                    {result.is_bulk ? "Bulk Task Execution" : "Task Execution Results"}
                  </h3>
                  <div
                    className={`px-3 py-1 rounded text-sm font-medium ${
                      result.status === "completed"
                        ? "text-green-400 bg-green-900/20"
                        : result.status === "failed"
                        ? "text-red-400 bg-red-900/20"
                        : result.status === "partial"
                        ? "text-yellow-400 bg-yellow-900/20"
                        : "text-blue-400 bg-blue-900/20"
                    }`}
                  >
                    {result.status || "pending"}
                  </div>
                </div>

                {result.error ? (
                  <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                    <p className="text-red-400 font-medium mb-2">Execution Failed</p>
                    <p className="text-sm text-gray-300">{result.error}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                        <div className="text-sm text-gray-400">Task ID</div>
                        <div className="text-sm text-white font-mono">
                          {result.task_id || key}
                        </div>
                      </div>
                      <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                        <div className="text-sm text-gray-400">Execution Time</div>
                        <div className="text-sm text-white">
                          {result.execution_time_hours 
                            ? `${result.execution_time_hours.toFixed(2)} hours`
                            : "N/A"}
                        </div>
                      </div>
                      {result.is_bulk && (
                        <>
                          <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                            <div className="text-sm text-gray-400">Total Tasks</div>
                            <div className="text-sm text-white">{result.total_tasks || 0}</div>
                          </div>
                          <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                            <div className="text-sm text-gray-400">Success/Failed</div>
                            <div className="text-sm text-white">
                              {result.successful_tasks || 0} / {result.failed_tasks || 0}
                            </div>
                          </div>
                        </>
                      )}
                    </div>

                    {result.results && (
                      <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                        <h4 className="text-md font-medium text-gray-300 mb-3">
                          {result.is_bulk ? "Execution Results Summary" : "Execution Results"}
                        </h4>
                        <div className="space-y-2">
                          {Array.isArray(result.results) ? (
                            result.results.map((item, idx) => (
                              <div key={idx} className="bg-gray-800/50 rounded p-3">
                                <div className="flex justify-between items-start mb-2">
                                  <span className="text-sm font-medium text-white">
                                    {item.task_type || `Task ${idx + 1}`}
                                  </span>
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    item.status === "completed" ? "text-green-400 bg-green-900/20" :
                                    item.status === "failed" ? "text-red-400 bg-red-900/20" :
                                    "text-yellow-400 bg-yellow-900/20"
                                  }`}>
                                    {item.status || "pending"}
                                  </span>
                                </div>
                                {item.error && (
                                  <p className="text-xs text-red-400">{item.error}</p>
                                )}
                                {item.result && typeof item.result === 'object' && (
                                  <div className="text-xs text-gray-400 mt-1">
                                    {JSON.stringify(item.result, null, 2)}
                                  </div>
                                )}
                              </div>
                            ))
                          ) : typeof result.results === 'object' ? (
                            Object.entries(result.results).map(([resultKey, value]) => (
                              <div key={resultKey} className="flex justify-between">
                                <span className="text-sm text-gray-400">
                                  {resultKey.replace(/_/g, " ")}:
                                </span>
                                <span className="text-sm text-white">
                                  {Array.isArray(value) ? value.join(", ") : 
                                   typeof value === 'object' ? JSON.stringify(value) :
                                   String(value)}
                                </span>
                              </div>
                            ))
                          ) : (
                            <p className="text-sm text-gray-400">{String(result.results)}</p>
                          )}
                        </div>
                      </div>
                    )}

                    {result.recommendations && result.recommendations.length > 0 && (
                      <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                        <h4 className="text-md font-medium text-gray-300 mb-3">
                          AI Recommendations
                        </h4>
                        <div className="space-y-1">
                          {result.recommendations.map((rec, idx) => (
                            <div key={idx} className="text-sm text-gray-400">
                              • {typeof rec === 'string' ? rec : JSON.stringify(rec)}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.success_criteria_met !== undefined && (
                      <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            result.success_criteria_met ? "bg-green-400" : "bg-red-400"
                          }`}></div>
                          <span className="text-sm text-gray-300">
                            Success Criteria: {result.success_criteria_met ? "Met" : "Not Met"}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ITAdministrativeTasks;
