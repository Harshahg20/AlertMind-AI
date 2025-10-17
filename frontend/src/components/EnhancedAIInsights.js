import React, { useState, useEffect } from "react";
import {
  Brain,
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  BarChart3,
  Zap,
  Shield,
  RefreshCw,
  Play,
  BookOpen,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";

const EnhancedAIInsights = ({ clientId = "client_001" }) => {
  const [agentStatus, setAgentStatus] = useState(null);
  const [agentInsights, setAgentInsights] = useState(null);
  const [agentPerformance, setAgentPerformance] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchEnhancedData();
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchEnhancedData, 30000);
    return () => clearInterval(interval);
  }, [clientId]);

  const fetchEnhancedData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [status, insights, performance, simulation] = await Promise.all([
        apiClient.getEnhancedAgentStatus(),
        apiClient.getEnhancedAgentInsights(),
        apiClient.getEnhancedAgentPerformance(),
        apiClient.simulateEnhancedAgent(clientId),
      ]);

      setAgentStatus(status);
      setAgentInsights(insights);
      setAgentPerformance(performance);
      setSimulationResult(simulation);
    } catch (err) {
      console.error("Error fetching enhanced AI data:", err);
      setError("Failed to load enhanced AI insights");
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return "text-green-400";
    if (confidence >= 0.6) return "text-yellow-400";
    return "text-red-400";
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency?.toLowerCase()) {
      case "critical":
        return "bg-red-900/20 text-red-400 border-red-500/30";
      case "high":
        return "bg-orange-900/20 text-orange-400 border-orange-500/30";
      case "medium":
        return "bg-yellow-900/20 text-yellow-400 border-yellow-500/30";
      case "low":
        return "bg-green-900/20 text-green-400 border-green-500/30";
      default:
        return "bg-gray-900/20 text-gray-400 border-gray-500/30";
    }
  };

  const getSystemHealthColor = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    if (score >= 40) return "text-orange-400";
    return "text-red-400";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
        <div className="flex items-center">
          <div className="text-red-400 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Brain className="w-6 h-6 mr-2" />
            Enhanced AI Insights
          </h2>
          <p className="text-gray-400 text-sm">
            Advanced cascade prediction with comprehensive data analysis
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-green-400 text-sm">AI Active</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-800/50 rounded-lg p-1">
        {[
          { id: "overview", label: "Overview", icon: BarChart3 },
          { id: "prediction", label: "Live Prediction", icon: Zap },
          { id: "performance", label: "Performance", icon: TrendingUp },
          { id: "insights", label: "AI Insights", icon: Brain },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
              activeTab === tab.id
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-700/50"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Agent Status Card */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Agent Status</h3>
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className="text-green-400 capitalize">
                  {agentStatus?.status || "Unknown"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">LLM Available:</span>
                <span
                  className={
                    agentStatus?.llm_available
                      ? "text-green-400"
                      : "text-red-400"
                  }
                >
                  {agentStatus?.llm_available ? "Yes" : "No"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Memory Size:</span>
                <span className="text-white">
                  {agentStatus?.memory_size || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Patterns Learned:</span>
                <span className="text-white">
                  {agentStatus?.patterns_learned || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Enhanced Features Card */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Enhanced Features
            </h3>
            <div className="space-y-2">
              {agentStatus?.enhanced_features &&
                Object.entries(agentStatus.enhanced_features).map(
                  ([feature, enabled]) => (
                    <div
                      key={feature}
                      className="flex items-center justify-between"
                    >
                      <span className="text-gray-400 text-sm capitalize">
                        {feature.replace(/_/g, " ")}
                      </span>
                      <div
                        className={`w-2 h-2 rounded-full ${
                          enabled ? "bg-green-400" : "bg-red-400"
                        }`}
                      ></div>
                    </div>
                  )
                )}
            </div>
          </div>

          {/* Performance Metrics Card */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Performance
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Predictions:</span>
                <span className="text-white">
                  {agentPerformance?.performance_metrics?.total_predictions ||
                    0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Avg Confidence:</span>
                <span
                  className={getConfidenceColor(
                    agentPerformance?.performance_metrics?.average_confidence ||
                      0
                  )}
                >
                  {(
                    (agentPerformance?.performance_metrics
                      ?.average_confidence || 0) * 100
                  ).toFixed(1)}
                  %
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Memory Usage:</span>
                <span className="text-white">
                  {agentPerformance?.memory_usage?.incident_memory_size || 0}{" "}
                  incidents
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "prediction" && simulationResult && (
        <div className="space-y-6">
          {/* Live Prediction Card */}
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">
                Live AI Prediction
              </h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-blue-400 text-sm">
                  Real-time Analysis
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-gray-400 text-sm">Predicted In</div>
                <div className="text-2xl font-bold text-white">
                  {simulationResult.prediction?.predicted_in || 0}m
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-gray-400 text-sm">Confidence</div>
                <div
                  className={`text-2xl font-bold ${getConfidenceColor(
                    simulationResult.prediction?.confidence || 0
                  )}`}
                >
                  {(
                    (simulationResult.prediction?.confidence || 0) * 100
                  ).toFixed(1)}
                  %
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-gray-400 text-sm">System Health</div>
                <div
                  className={`text-2xl font-bold ${getSystemHealthColor(
                    simulationResult.system_health_score || 0
                  )}`}
                >
                  {simulationResult.system_health_score || 0}/100
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <div className="text-gray-400 text-sm">Data Sources</div>
                <div className="text-2xl font-bold text-white">
                  {simulationResult.data_sources_count || 0}
                </div>
              </div>
            </div>

            <div
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getUrgencyColor(
                simulationResult.prediction?.urgency_level
              )}`}
            >
              {simulationResult.prediction?.urgency_level?.toUpperCase() ||
                "UNKNOWN"}{" "}
              URGENCY
            </div>
          </div>

          {/* Root Causes */}
          {simulationResult.prediction?.root_causes && (
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-white mb-4">
                Root Causes Identified
              </h4>
              <div className="space-y-2">
                {simulationResult.prediction.root_causes.map((cause, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-300">{cause}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prevention Actions */}
          {simulationResult.prediction?.prevention_actions && (
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-white mb-4">
                Recommended Actions
              </h4>
              <div className="space-y-3">
                {simulationResult.prediction.prevention_actions.map(
                  (action, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-white text-xs font-bold">
                          {index + 1}
                        </span>
                      </div>
                      <span className="text-gray-300">{action}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {/* Enhanced Analysis Details */}
          {simulationResult.prediction?.enhanced_analysis && (
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-white mb-4">
                Enhanced Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Comprehensive Data:</span>
                    <span
                      className={
                        simulationResult.prediction.enhanced_analysis
                          .comprehensive_data_used
                          ? "text-green-400"
                          : "text-red-400"
                      }
                    >
                      {simulationResult.prediction.enhanced_analysis
                        .comprehensive_data_used
                        ? "Yes"
                        : "No"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Trend Analysis:</span>
                    <span
                      className={
                        simulationResult.prediction.enhanced_analysis
                          .trend_analysis_available
                          ? "text-green-400"
                          : "text-red-400"
                      }
                    >
                      {simulationResult.prediction.enhanced_analysis
                        .trend_analysis_available
                        ? "Available"
                        : "Unavailable"}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">External Factors:</span>
                    <span
                      className={
                        simulationResult.prediction.enhanced_analysis
                          .external_factors_considered
                          ? "text-green-400"
                          : "text-red-400"
                      }
                    >
                      {simulationResult.prediction.enhanced_analysis
                        .external_factors_considered
                        ? "Considered"
                        : "Not Considered"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">LLM Quality:</span>
                    <span className="text-blue-400 capitalize">
                      {simulationResult.prediction.enhanced_analysis
                        .llm_analysis_quality || "Unknown"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "performance" && agentPerformance && (
        <div className="space-y-6">
          {/* Performance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-2">
                Total Predictions
              </div>
              <div className="text-3xl font-bold text-white">
                {agentPerformance.performance_metrics?.total_predictions || 0}
              </div>
            </div>
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-2">
                Average Confidence
              </div>
              <div
                className={`text-3xl font-bold ${getConfidenceColor(
                  agentPerformance.performance_metrics?.average_confidence || 0
                )}`}
              >
                {(
                  (agentPerformance.performance_metrics?.average_confidence ||
                    0) * 100
                ).toFixed(1)}
                %
              </div>
            </div>
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-2">Memory Usage</div>
              <div className="text-3xl font-bold text-white">
                {agentPerformance.memory_usage?.incident_memory_size || 0}
              </div>
            </div>
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
              <div className="text-gray-400 text-sm mb-2">
                Learning Progress
              </div>
              <div className="text-3xl font-bold text-white">
                {agentPerformance.learning_progress?.patterns_learned || 0}
              </div>
            </div>
          </div>

          {/* Enhanced Features Status */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-white mb-4">
              Enhanced Features Status
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agentPerformance.enhanced_features_status &&
                Object.entries(agentPerformance.enhanced_features_status).map(
                  ([feature, enabled]) => (
                    <div
                      key={feature}
                      className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg"
                    >
                      <span className="text-gray-300 text-sm capitalize">
                        {feature.replace(/_/g, " ")}
                      </span>
                      <div
                        className={`w-3 h-3 rounded-full ${
                          enabled ? "bg-green-400" : "bg-red-400"
                        }`}
                      ></div>
                    </div>
                  )
                )}
            </div>
          </div>
        </div>
      )}

      {activeTab === "insights" && agentInsights && (
        <div className="space-y-6">
          {/* Learning Summary */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-white mb-4">
              AI Learning Summary
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400 mb-2">
                  {agentInsights.total_incidents_analyzed || 0}
                </div>
                <div className="text-gray-400 text-sm">Incidents Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {agentInsights.patterns_learned || 0}
                </div>
                <div className="text-gray-400 text-sm">Patterns Learned</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400 mb-2">
                  {(
                    (agentInsights.agent_learning_summary
                      ?.confidence_improvement || 0) * 100
                  ).toFixed(1)}
                  %
                </div>
                <div className="text-gray-400 text-sm">
                  Confidence Improvement
                </div>
              </div>
            </div>
          </div>

          {/* Recent Incidents */}
          {agentInsights.recent_incidents &&
            agentInsights.recent_incidents.length > 0 && (
              <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-white mb-4">
                  Recent Incidents
                </h4>
                <div className="space-y-3">
                  {agentInsights.recent_incidents.map((incident, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg"
                    >
                      <div>
                        <div className="text-white text-sm">
                          {new Date(incident.timestamp).toLocaleString()}
                        </div>
                        <div className="text-gray-400 text-xs">
                          Client: {incident.client_id} | Confidence:{" "}
                          {((incident.confidence || 0) * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getUrgencyColor(
                          incident.urgency
                        )}`}
                      >
                        {incident.urgency?.toUpperCase() || "UNKNOWN"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
};

export default EnhancedAIInsights;
