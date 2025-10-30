import React, { useState, useEffect } from "react";
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
} from "lucide-react";
import { apiClient } from "../utils/apiClient";
import { ITAdminSkeleton } from "./SkeletonLoader";

const ITAdministrativeTasks = ({ clients = [], loading = false }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  const [taskRecommendations, setTaskRecommendations] = useState({});
  const [taskHistory, setTaskHistory] = useState({});
  const [complianceReports, setComplianceReports] = useState({});
  const [availableTasks, setAvailableTasks] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [activeTab, setActiveTab] = useState("recommendations");
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [executionResults, setExecutionResults] = useState({});

  useEffect(() => {
    if (clients.length > 0) {
      fetchAvailableTasks();
      fetchTaskRecommendations();
    }
  }, [clients]);

  const fetchAvailableTasks = async () => {
    try {
      const response = await apiClient.get("/api/it-admin/available-tasks");
      setAvailableTasks(response.data.available_task_types || []);
    } catch (error) {
      console.error("Error fetching available tasks:", error);
    }
  };

  const fetchTaskRecommendations = async () => {
    const clientId = selectedClient === "all" ? clients[0]?.id : selectedClient;
    if (!clientId) return;

    try {
      setLoadingData(true);
      const response = await apiClient.get(
        `/api/it-admin/recommendations/${clientId}`
      );
      setTaskRecommendations((prev) => ({
        ...prev,
        [clientId]: response.data.recommended_tasks,
      }));
    } catch (error) {
      console.error("Error fetching task recommendations:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const fetchTaskHistory = async (clientId) => {
    try {
      const response = await apiClient.get(
        `/api/it-admin/task-history/${clientId}`
      );
      setTaskHistory((prev) => ({
        ...prev,
        [clientId]: response.data.task_history,
      }));
    } catch (error) {
      console.error("Error fetching task history:", error);
    }
  };

  const generateComplianceReport = async (clientId) => {
    try {
      setLoadingData(true);
      const response = await apiClient.get(
        `/api/it-admin/compliance-report/${clientId}`
      );
      setComplianceReports((prev) => ({
        ...prev,
        [clientId]: response.data.compliance_report,
      }));
    } catch (error) {
      console.error("Error generating compliance report:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const executeTask = async (clientId, taskType, priority = "medium") => {
    try {
      setLoadingData(true);
      const response = await apiClient.post(
        `/api/it-admin/execute/${clientId}`,
        {
          task_type: taskType,
          priority: priority,
        }
      );
      setExecutionResults((prev) => ({
        ...prev,
        [`${clientId}_${taskType}_${Date.now()}`]: response.data.task_execution,
      }));
    } catch (error) {
      console.error("Error executing task:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const bulkExecuteTasks = async (clientId, taskTypes) => {
    try {
      setLoadingData(true);
      const response = await apiClient.post(
        `/api/it-admin/bulk-execute/${clientId}`,
        {
          task_types: taskTypes,
        }
      );
      setExecutionResults((prev) => ({
        ...prev,
        [`${clientId}_bulk_${Date.now()}`]: response.data.bulk_execution,
      }));
    } catch (error) {
      console.error("Error bulk executing tasks:", error);
    } finally {
      setLoadingData(false);
    }
  };

  const handleTaskSelection = (taskType, selected) => {
    if (selected) {
      setSelectedTasks((prev) => [...prev, taskType]);
    } else {
      setSelectedTasks((prev) => prev.filter((type) => type !== taskType));
    }
  };

  const handleBulkExecute = async () => {
    const clientId = selectedClient === "all" ? clients[0]?.id : selectedClient;
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

  if (loading || loadingData) {
    return <ITAdminSkeleton />;
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
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
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
          {Object.entries(taskRecommendations).map(([clientId, tasks]) => (
            <div
              key={clientId}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  AI Task Recommendations
                </h3>
                <div className="text-sm text-gray-400">
                  {tasks.length} recommendations
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tasks.map((task) => {
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
                })}
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
          ))}
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
                              ? clients[0]?.id
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
          {filteredClients.map((client) => (
            <div
              key={client.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Task History - {client.name}
                </h3>
                <button
                  onClick={() => fetchTaskHistory(client.id)}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded transition-colors"
                >
                  Load History
                </button>
              </div>

              {taskHistory[client.id] ? (
                <div className="space-y-3">
                  {taskHistory[client.id].map((task, idx) => {
                    const IconComponent = getTaskIcon(task.task_type);
                    return (
                      <div
                        key={idx}
                        className="bg-gray-700/50 border border-gray-600 rounded-lg p-3"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <IconComponent className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-medium text-white">
                              {task.task_type.replace(/_/g, " ").toUpperCase()}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div
                              className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                                task.priority
                              )}`}
                            >
                              {task.priority}
                            </div>
                            <div
                              className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                                task.status
                              )}`}
                            >
                              {task.status}
                            </div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-400">
                          {task.description} •{" "}
                          {new Date(task.created_at).toLocaleString()}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <Clock className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p>No task history available</p>
                  <p className="text-sm mt-2">
                    Click "Load History" to fetch task history
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Compliance Tab */}
      {activeTab === "compliance" && (
        <div className="space-y-6">
          {filteredClients.map((client) => (
            <div
              key={client.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Compliance Report - {client.name}
                </h3>
                <button
                  onClick={() => generateComplianceReport(client.id)}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Generate Report
                </button>
              </div>

              {complianceReports[client.id] ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white">
                        {(
                          complianceReports[client.id].compliance_score * 100
                        ).toFixed(1)}
                        %
                      </div>
                      <div className="text-sm text-gray-400">
                        Compliance Score
                      </div>
                    </div>
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <div className="text-lg font-semibold text-white">
                        {complianceReports[
                          client.id
                        ].overall_status.toUpperCase()}
                      </div>
                      <div className="text-sm text-gray-400">
                        Overall Status
                      </div>
                    </div>
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <div className="text-lg font-semibold text-white">
                        {complianceReports[
                          client.id
                        ].risk_assessment.toUpperCase()}
                      </div>
                      <div className="text-sm text-gray-400">
                        Risk Assessment
                      </div>
                    </div>
                  </div>

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
                                {area.area.replace(/_/g, " ").toUpperCase()}
                              </div>
                              <div className="text-xs text-gray-400">
                                Last checked:{" "}
                                {new Date(
                                  area.last_checked
                                ).toLocaleDateString()}
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <div className="text-sm text-white">
                                {(area.score * 100).toFixed(1)}%
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
                                {area.status}
                              </div>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <Shield className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p>No compliance report available</p>
                  <p className="text-sm mt-2">
                    Click "Generate Report" to create a compliance report
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Execution Tab */}
      {activeTab === "execution" && (
        <div className="space-y-6">
          {Object.entries(executionResults).map(([key, result]) => (
            <div
              key={key}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  Task Execution Results
                </h3>
                <div
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    result.status === "completed"
                      ? "text-green-400 bg-green-900/20"
                      : result.status === "failed"
                      ? "text-red-400 bg-red-900/20"
                      : "text-yellow-400 bg-yellow-900/20"
                  }`}
                >
                  {result.status}
                </div>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                    <div className="text-sm text-gray-400">Task ID</div>
                    <div className="text-sm text-white font-mono">
                      {result.task_id}
                    </div>
                  </div>
                  <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-3">
                    <div className="text-sm text-gray-400">Execution Time</div>
                    <div className="text-sm text-white">
                      {result.execution_time_hours?.toFixed(2)} hours
                    </div>
                  </div>
                </div>

                {result.results && (
                  <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                    <h4 className="text-md font-medium text-gray-300 mb-3">
                      Execution Results
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(result.results).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-sm text-gray-400">
                            {key.replace(/_/g, " ")}:
                          </span>
                          <span className="text-sm text-white">
                            {Array.isArray(value) ? value.join(", ") : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.recommendations &&
                  result.recommendations.length > 0 && (
                    <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                      <h4 className="text-md font-medium text-gray-300 mb-3">
                        AI Recommendations
                      </h4>
                      <div className="space-y-1">
                        {result.recommendations.map((rec, idx) => (
                          <div key={idx} className="text-sm text-gray-400">
                            • {rec}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            </div>
          ))}

          {Object.keys(executionResults).length === 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="text-center text-gray-400 py-8">
                <Play className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                <p>No task executions to display</p>
                <p className="text-sm mt-2">
                  Execute tasks to see results here
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ITAdministrativeTasks;
