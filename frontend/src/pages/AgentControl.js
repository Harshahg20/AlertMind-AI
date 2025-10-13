import React, { useState, useEffect } from "react";
import { apiClient } from "../utils/apiClient";

const AgentControl = () => {
  const [agentStatus, setAgentStatus] = useState(null);
  const [agentMetrics, setAgentMetrics] = useState(null);
  const [agentInsights, setAgentInsights] = useState(null);
  const [agentPredictions, setAgentPredictions] = useState([]);
  // removed: playbook/patch state (moved to Ops Console)
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchAgentData();
    const interval = setInterval(fetchAgentData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAgentData = async () => {
    try {
      const [status, insights, predictions] = await Promise.all([
        apiClient.getAgentStatus(),
        apiClient.getAgentInsights(),
        apiClient.getAgentPredictions(),
      ]);

      setAgentStatus(status);
      setAgentMetrics(status.agent_metrics);
      setAgentInsights(status.agent_insights);
      setAgentPredictions(predictions.predictions || []);
    } catch (error) {
      console.error("Error fetching agent data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartAgent = async () => {
    setActionLoading(true);
    try {
      await apiClient.startAgent();
      await fetchAgentData();
    } catch (error) {
      console.error("Error starting agent:", error);
      alert("Failed to start agent");
    } finally {
      setActionLoading(false);
    }
  };

  const handleStopAgent = async () => {
    setActionLoading(true);
    try {
      await apiClient.stopAgent();
      await fetchAgentData();
    } catch (error) {
      console.error("Error stopping agent:", error);
      alert("Failed to stop agent");
    } finally {
      setActionLoading(false);
    }
  };

  const handleTriggerLearning = async () => {
    setActionLoading(true);
    try {
      await apiClient.triggerAgentLearning();
      await fetchAgentData();
    } catch (error) {
      console.error("Error triggering learning:", error);
      alert("Failed to trigger learning");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSimulateCascade = async (scenarioType) => {
    setActionLoading(true);
    try {
      await apiClient.simulateCascade({
        client_id: "client_001",
        type: scenarioType,
      });
      await fetchAgentData();
    } catch (error) {
      console.error("Error simulating cascade:", error);
      alert("Failed to simulate cascade");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Agent Status Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center">
              <span className="mr-2">🤖</span>
              Autonomous AI Agent Control
            </h2>
            <p className="text-gray-400 text-sm">
              Control and monitor the cascade prevention AI agent
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleStartAgent}
              disabled={actionLoading || agentStatus?.agent_running}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
            >
              {actionLoading ? "Starting..." : "Start Agent"}
            </button>
            <button
              onClick={handleStopAgent}
              disabled={actionLoading || !agentStatus?.agent_running}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors"
            >
              {actionLoading ? "Stopping..." : "Stop Agent"}
            </button>
          </div>
        </div>

        {/* Agent Status Indicators */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-gray-700/30 rounded">
            <div className="text-lg font-bold text-white">
              {agentStatus?.agent_running ? "🟢" : "🔴"}
            </div>
            <div className="text-xs text-gray-400">
              {agentStatus?.agent_running ? "Running" : "Stopped"}
            </div>
          </div>
          <div className="text-center p-3 bg-gray-700/30 rounded">
            <div className="text-lg font-bold text-blue-400">
              {agentMetrics?.total_actions_taken || 0}
            </div>
            <div className="text-xs text-gray-400">Actions Taken</div>
          </div>
          <div className="text-center p-3 bg-gray-700/30 rounded">
            <div className="text-lg font-bold text-green-400">
              {agentMetrics?.success_rate || 0}%
            </div>
            <div className="text-xs text-gray-400">Success Rate</div>
          </div>
          <div className="text-center p-3 bg-gray-700/30 rounded">
            <div className="text-lg font-bold text-purple-400">
              {agentMetrics?.learning_cycles || 0}
            </div>
            <div className="text-xs text-gray-400">Learning Cycles</div>
          </div>
        </div>
      </div>

      {/* Agent Metrics */}
      {agentMetrics && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <span className="mr-2">📊</span>
            Agent Performance Metrics
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-700/20 rounded">
              <div className="text-sm text-gray-400 mb-1">Agent State</div>
              <div className="text-white font-semibold capitalize">
                {agentMetrics.agent_state}
              </div>
            </div>
            <div className="p-4 bg-gray-700/20 rounded">
              <div className="text-sm text-gray-400 mb-1">
                Confidence Threshold
              </div>
              <div className="text-white font-semibold">
                {(agentMetrics.confidence_threshold * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-gray-700/20 rounded">
              <div className="text-sm text-gray-400 mb-1">Risk Tolerance</div>
              <div className="text-white font-semibold">
                {(agentMetrics.risk_tolerance * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-gray-700/20 rounded">
              <div className="text-sm text-gray-400 mb-1">Active Clients</div>
              <div className="text-white font-semibold">
                {agentMetrics.active_clients}
              </div>
            </div>
            <div className="p-4 bg-gray-700/20 rounded">
              <div className="text-sm text-gray-400 mb-1">Patterns Learned</div>
              <div className="text-white font-semibold">
                {agentMetrics.patterns_learned}
              </div>
            </div>
            <div className="p-4 bg-gray-700/20 rounded">
              <div className="text-sm text-gray-400 mb-1">Recent Decisions</div>
              <div className="text-white font-semibold">
                {agentMetrics.recent_decisions}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Insights */}
      {agentInsights && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <span className="mr-2">🧠</span>
            AI Agent Insights
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-md font-semibold text-gray-300 mb-3">
                Agent Personality
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Tolerance:</span>
                  <span className="text-white capitalize">
                    {agentInsights.agent_personality?.risk_tolerance}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Learning Speed:</span>
                  <span className="text-white capitalize">
                    {agentInsights.agent_personality?.learning_speed}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Confidence Level:</span>
                  <span className="text-white capitalize">
                    {agentInsights.agent_personality?.confidence_level}
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-md font-semibold text-gray-300 mb-3">
                Performance Analysis
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Success Rate:</span>
                  <span className="text-white">
                    {agentInsights.performance_analysis?.success_rate}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Efficiency:</span>
                  <span className="text-white capitalize">
                    {agentInsights.performance_analysis?.efficiency}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Reliability:</span>
                  <span className="text-white capitalize">
                    {agentInsights.performance_analysis?.reliability}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {agentInsights.recommendations &&
            agentInsights.recommendations.length > 0 && (
              <div className="mt-6">
                <h4 className="text-md font-semibold text-gray-300 mb-3">
                  AI Recommendations
                </h4>
                <div className="space-y-2">
                  {agentInsights.recommendations.map((rec, index) => (
                    <div
                      key={index}
                      className="p-3 bg-blue-900/20 border border-blue-500/20 rounded"
                    >
                      <div className="text-sm text-blue-300">💡 {rec}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
        </div>
      )}

      {/* Agent Predictions */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <span className="mr-2">🔮</span>
            Active Cascade Predictions
          </h3>
          <button
            onClick={handleTriggerLearning}
            disabled={actionLoading}
            className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm rounded transition-colors"
          >
            {actionLoading ? "Learning..." : "Trigger Learning"}
          </button>
        </div>

        {agentPredictions.length > 0 ? (
          <div className="space-y-3">
            {agentPredictions.slice(0, 5).map((prediction, index) => (
              <div
                key={index}
                className="p-4 bg-gradient-to-r from-orange-900/20 to-red-900/20 border border-orange-500/30 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse"></div>
                    <span className="font-semibold text-white">
                      {prediction.client_name}
                    </span>
                    <span className="text-sm text-gray-400">•</span>
                    <span className="text-sm text-gray-300">
                      {prediction.predicted_cascade_systems?.join(", ")}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-orange-600 text-white text-xs rounded-full">
                      {Math.round(prediction.prediction_confidence * 100)}%
                      confidence
                    </span>
                    <span className="px-2 py-1 bg-red-600 text-white text-xs rounded-full">
                      {prediction.time_to_cascade_minutes}min
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-300">
                  {prediction.ai_analysis?.root_cause_analysis}
                </div>
                {prediction.recommended_actions &&
                  prediction.recommended_actions.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs text-gray-400 mb-1">
                        Recommended Actions:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {prediction.recommended_actions
                          .slice(0, 3)
                          .map((action, i) => (
                            <span
                              key={i}
                              className="px-2 py-1 bg-blue-600 text-white text-xs rounded"
                            >
                              {action.action}
                            </span>
                          ))}
                      </div>
                    </div>
                  )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            <span className="text-4xl mb-2 block">🤖</span>
            <p>No active cascade predictions</p>
            <p className="text-sm">
              Agent is monitoring for potential cascades
            </p>
          </div>
        )}
      </div>

      {/* Simulation Controls */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <span className="mr-2">🧪</span>
          Cascade Simulation Testing
        </h3>
        <p className="text-gray-400 text-sm mb-4">
          Test the agent's response to different cascade scenarios
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => handleSimulateCascade("database_cascade")}
            disabled={actionLoading}
            className="p-4 bg-red-900/20 border border-red-500/30 rounded hover:bg-red-900/30 disabled:opacity-50 transition-colors"
          >
            <div className="text-red-400 font-semibold">Database Cascade</div>
            <div className="text-xs text-gray-400 mt-1">
              CPU overload scenario
            </div>
          </button>

          <button
            onClick={() => handleSimulateCascade("network_cascade")}
            disabled={actionLoading}
            className="p-4 bg-blue-900/20 border border-blue-500/30 rounded hover:bg-blue-900/30 disabled:opacity-50 transition-colors"
          >
            <div className="text-blue-400 font-semibold">Network Cascade</div>
            <div className="text-xs text-gray-400 mt-1">
              Packet loss scenario
            </div>
          </button>

          <button
            onClick={() => handleSimulateCascade("storage_cascade")}
            disabled={actionLoading}
            className="p-4 bg-green-900/20 border border-green-500/30 rounded hover:bg-green-900/30 disabled:opacity-50 transition-colors"
          >
            <div className="text-green-400 font-semibold">Storage Cascade</div>
            <div className="text-xs text-gray-400 mt-1">
              Disk space scenario
            </div>
          </button>

          <button
            onClick={() => handleSimulateCascade("application_cascade")}
            disabled={actionLoading}
            className="p-4 bg-purple-900/20 border border-purple-500/30 rounded hover:bg-purple-900/30 disabled:opacity-50 transition-colors"
          >
            <div className="text-purple-400 font-semibold">
              Application Cascade
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Service failure scenario
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentControl;
