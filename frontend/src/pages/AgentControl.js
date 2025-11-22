import React, { useState, useEffect } from "react";
import { apiClient } from "../utils/apiClient";

const AgentControl = () => {
  // Initialize with optimistic defaults for instant UI render
  const [agentStatus, setAgentStatus] = useState({
    agent_running: false,
    agent_metrics: {
      total_actions_taken: 0,
      success_rate: 0,
      learning_cycles: 0,
      agent_state: "stopped",
      confidence_threshold: 0.7,
      risk_tolerance: 0.6,
      active_clients: 0,
      patterns_learned: 0,
      recent_decisions: 0,
    },
  });
  const [agentMetrics, setAgentMetrics] = useState(agentStatus?.agent_metrics || {});
  const [agentInsights, setAgentInsights] = useState({
    agent_personality: {
      risk_tolerance: "moderate",
      learning_speed: "normal",
      confidence_level: "medium",
    },
    performance_analysis: {
      success_rate: "0%",
      efficiency: "unknown",
      reliability: "unknown",
    },
    recommendations: [],
  });
  const [agentPredictions, setAgentPredictions] = useState([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [showRecommendationModal, setShowRecommendationModal] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState(null);

  // Add loading state to prevent concurrent requests
  const isFetchingRef = React.useRef(false);
  const insightsRefreshCounter = React.useRef(0);
  const lastFetchTimeRef = React.useRef(0);
  
  // Ultra-optimized fetch - minimal blocking, maximum async
  const fetchAgentData = React.useCallback(async () => {
    // Prevent concurrent requests
    if (isFetchingRef.current) {
      return;
    }
    
    // Throttle: Don't fetch if last fetch was less than 5 seconds ago
    const now = Date.now();
    if (now - lastFetchTimeRef.current < 5000) {
      return;
    }
    
    isFetchingRef.current = true;
    lastFetchTimeRef.current = now;
    
    // Set default optimistic state immediately for fast UI
    setConnectionStatus("connecting");
    
    // CRITICAL: Only fetch status immediately, everything else is deferred
    try {
      const statusResult = await Promise.race([
        apiClient.getAgentStatus(),
        new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), 5000)) // 5s timeout
      ]).catch(() => null);
      
      if (statusResult) {
        setAgentStatus(statusResult);
        setAgentMetrics(statusResult?.agent_metrics || {});
        setConnectionStatus("connected");
        // Use insights from status if available (no extra API call)
        if (statusResult?.agent_insights) {
          setAgentInsights(statusResult.agent_insights);
        }
      } else {
        setConnectionStatus("disconnected");
      }
    } catch (error) {
      console.error("Error fetching agent status:", error);
      setConnectionStatus("disconnected");
    } finally {
      isFetchingRef.current = false;
    }
    
    // DEFER ALL HEAVY OPERATIONS - don't block UI
    // Run these completely async with no waiting
    setTimeout(() => {
      // Heavy: Fetch predictions (with timeout)
      Promise.race([
        apiClient.getAgentPredictions(),
        new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), 3000))
      ])
        .then((result) => {
          if (result?.predictions) {
            setAgentPredictions(result.predictions || []);
          }
        })
        .catch(() => {
          // Silently fail - not critical
        });
      
      // Heavy: Fetch training status (with timeout)
      Promise.race([
        apiClient.getTrainingStatus(),
        new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), 3000))
      ])
        .then((result) => {
          if (result) setTrainingStatus(result);
        })
        .catch(() => {
          // Silently fail - not critical
        });
      
      // Expensive: Fetch insights VERY rarely (every 5th call, ~4 minutes)
      insightsRefreshCounter.current += 1;
      if (insightsRefreshCounter.current % 5 === 0) {
        Promise.race([
          apiClient.getAgentInsights(),
          new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), 5000))
        ])
          .then((insights) => {
            if (insights) setAgentInsights(insights);
          })
          .catch(() => {
            // Silently fail - not critical
          });
      }
    }, 100); // Small delay to let UI render first
  }, []);
  
  useEffect(() => {
    // Initial fast fetch (status only)
    fetchAgentData();
    
    // Much longer interval - only refresh every 60 seconds (was 30)
    // DISABLED: Auto-refresh commented out to allow services to scale to zero
    // Uncomment for demo mode to enable real-time updates
    // const interval = setInterval(() => {
    //   fetchAgentData();
    // }, 60000); // Update every 60 seconds
    
    // return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const handleStartAgent = async () => {
    setActionLoading(true);
    try {
      await apiClient.startAgent();

      // Update local state immediately
      setAgentStatus((prev) => ({
        ...prev,
        agent_running: true,
        agent_metrics: {
          ...prev.agent_metrics,
          agent_state: "active",
        },
      }));

      // Refresh data from server
      await fetchAgentData();
    } catch (error) {
      console.error("Error starting agent:", error);
      alert("Failed to start agent: " + (error.message || "Unknown error"));
    } finally {
      setActionLoading(false);
    }
  };

  const handleStopAgent = async () => {
    setActionLoading(true);
    try {
      await apiClient.stopAgent();

      // Update local state immediately
      setAgentStatus((prev) => ({
        ...prev,
        agent_running: false,
        agent_metrics: {
          ...prev.agent_metrics,
          agent_state: "stopped",
        },
      }));

      // Refresh data from server
      await fetchAgentData();
    } catch (error) {
      console.error("Error stopping agent:", error);
      alert("Failed to stop agent: " + (error.message || "Unknown error"));
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

  const handleRecommendationClick = (recommendation, index) => {
    const recommendationDetails = {
      id: index,
      title: recommendation,
      priority: index === 0 ? "High" : index === 1 ? "Medium" : "Low",
      category: getRecommendationCategory(recommendation),
      impact: getRecommendationImpact(recommendation),
      effort: getRecommendationEffort(recommendation),
      description: getRecommendationDescription(recommendation),
      actions: getRecommendationActions(recommendation),
      metrics: getRecommendationMetrics(recommendation),
      timeline: getRecommendationTimeline(recommendation),
    };

    setSelectedRecommendation(recommendationDetails);
    setShowRecommendationModal(true);
  };

  const getRecommendationCategory = (rec) => {
    if (rec.toLowerCase().includes("monitoring")) return "Monitoring";
    if (rec.toLowerCase().includes("pattern")) return "Learning";
    if (rec.toLowerCase().includes("confidence")) return "Performance";
    if (rec.toLowerCase().includes("expand")) return "Capability";
    return "General";
  };

  const getRecommendationImpact = (rec) => {
    if (rec.toLowerCase().includes("monitoring")) return "High";
    if (rec.toLowerCase().includes("pattern")) return "Medium";
    if (rec.toLowerCase().includes("confidence")) return "High";
    return "Medium";
  };

  const getRecommendationEffort = (rec) => {
    if (rec.toLowerCase().includes("monitoring")) return "Low";
    if (rec.toLowerCase().includes("pattern")) return "Medium";
    if (rec.toLowerCase().includes("confidence")) return "Low";
    return "Medium";
  };

  const getRecommendationDescription = (rec) => {
    const descriptions = {
      "Continue monitoring system performance":
        "Maintain continuous oversight of system health metrics, alert patterns, and performance indicators to ensure early detection of potential issues.",
      "Consider expanding pattern recognition":
        "Enhance the AI agent's ability to identify complex failure patterns across multiple systems and clients for improved prediction accuracy.",
      "Maintain current confidence thresholds":
        "Keep existing confidence levels for cascade predictions to balance between false positives and missed detections.",
    };
    return (
      descriptions[rec] ||
      "Detailed analysis and implementation guidance for this recommendation."
    );
  };

  const getRecommendationActions = (rec) => {
    const actions = {
      "Continue monitoring system performance": [
        "Review current monitoring dashboards",
        "Set up automated alerts for key metrics",
        "Schedule regular performance reviews",
        "Update monitoring thresholds based on trends",
      ],
      "Consider expanding pattern recognition": [
        "Analyze historical incident data",
        "Implement advanced ML algorithms",
        "Cross-train on multiple client environments",
        "Validate pattern accuracy with real incidents",
      ],
      "Maintain current confidence thresholds": [
        "Review recent prediction accuracy",
        "Analyze false positive/negative rates",
        "Adjust thresholds based on business impact",
        "Document threshold rationale",
      ],
    };
    return (
      actions[rec] || [
        "Review recommendation details",
        "Plan implementation approach",
        "Execute recommended actions",
      ]
    );
  };

  const getRecommendationMetrics = (rec) => {
    return (
      {
        "Continue monitoring system performance": {
          "Detection Time": "Improve by 15-20%",
          "False Positives": "Reduce by 10%",
          "System Uptime": "Increase by 5%",
        },
        "Consider expanding pattern recognition": {
          "Prediction Accuracy": "Improve by 25-30%",
          "Pattern Coverage": "Expand by 40%",
          "Learning Speed": "Increase by 20%",
        },
        "Maintain current confidence thresholds": {
          "Prediction Stability": "Maintain 95%+",
          "User Trust": "Sustain high levels",
          "System Reliability": "Keep consistent",
        },
      }[rec] || {
        "Overall Impact": "Positive",
        "Implementation Risk": "Low",
        ROI: "High",
      }
    );
  };

  const getRecommendationTimeline = (rec) => {
    if (rec.toLowerCase().includes("monitoring")) return "1-2 weeks";
    if (rec.toLowerCase().includes("pattern")) return "4-6 weeks";
    if (rec.toLowerCase().includes("confidence")) return "Immediate";
    return "2-4 weeks";
  };

  const executeRecommendation = async (recommendation) => {
    setActionLoading(true);
    try {
      // Simulate recommendation execution
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Trigger learning to incorporate the recommendation
      await apiClient.triggerAgentLearning();

      // Refresh data
      await fetchAgentData();

      alert(
        `Recommendation "${recommendation.title}" has been executed successfully!`
      );
      setShowRecommendationModal(false);
    } catch (error) {
      console.error("Error executing recommendation:", error);
      alert("Failed to execute recommendation");
    } finally {
      setActionLoading(false);
    }
  };

  // No blocking skeleton - UI renders immediately with optimistic defaults

  return (
    <div className="space-y-6">
      {/* Agent Management Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center">
              <span className="mr-2">🤖</span>
              Agent Management Console
            </h2>
            <p className="text-gray-400 text-sm">
              Control and monitor the cascade prevention AI agents
            </p>
            {/* Status info */}
            <div
              className={`text-xs mt-2 ${
                connectionStatus === "connected"
                  ? "text-green-400"
                  : connectionStatus === "disconnected"
                  ? "text-red-400"
                  : "text-yellow-400"
              }`}
            >
              Status:{" "}
              {connectionStatus === "connected" ? "Connected" : "Disconnected"}
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={async () => {
                if (actionLoading) {
                  return;
                }

                if (agentStatus?.agent_running) {
                  await handleStopAgent();
                } else {
                  await handleStartAgent();
                }
              }}
              disabled={actionLoading}
              className={`px-6 py-2 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded transition-colors font-medium ${
                agentStatus?.agent_running
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-green-600 hover:bg-green-700"
              }`}
            >
              {actionLoading
                ? agentStatus?.agent_running
                  ? "Stopping Training..."
                  : "Starting Training..."
                : agentStatus?.agent_running
                ? "Stop Agent Training"
                : "Start Agent Training"}
            </button>
          </div>
        </div>

        {/* Training Status Section */}
        {trainingStatus && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <span className="mr-2">🎯</span>
                Training Status
              </h3>
              <div
                className={`flex items-center space-x-2 text-sm ${
                  trainingStatus.training_active
                    ? "text-green-400"
                    : "text-gray-400"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    trainingStatus.training_active
                      ? "bg-green-400 animate-pulse"
                      : "bg-gray-400"
                  }`}
                ></div>
                <span>
                  {trainingStatus.training_active
                    ? "Training Active"
                    : "Training Stopped"}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">
                  Training Cycles
                </div>
                <div className="text-lg font-bold text-white">
                  {trainingStatus.total_training_cycles || 0}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">
                  Incidents Processed
                </div>
                <div className="text-lg font-bold text-white">
                  {trainingStatus.training_progress?.incidents_processed || 0}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">
                  Average Confidence
                </div>
                <div className="text-lg font-bold text-white">
                  {Math.round(
                    (trainingStatus.training_progress?.average_confidence ||
                      0) * 100
                  )}
                  %
                </div>
              </div>
            </div>

            {trainingStatus.last_training_cycle && (
              <div className="mt-3 text-xs text-gray-400">
                Last training cycle:{" "}
                {new Date(trainingStatus.last_training_cycle).toLocaleString()}
              </div>
            )}
          </div>
        )}

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

      {/* Enhanced Agent Insights */}
      {agentInsights && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <span className="mr-2">🧠</span>
              AI Agent Insights
            </h3>
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Live Analysis</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Agent Personality with Visual Indicators */}
            <div className="space-y-4">
              <h4 className="text-md font-semibold text-gray-300 mb-3 flex items-center">
                <span className="mr-2">🎭</span>
                Agent Personality
              </h4>

              {/* Risk Tolerance with Progress Bar */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Risk Tolerance</span>
                  <span className="text-white text-sm font-medium capitalize">
                    {agentInsights.agent_personality?.risk_tolerance}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      agentInsights.agent_personality?.risk_tolerance === "low"
                        ? "bg-green-500 w-1/3"
                        : agentInsights.agent_personality?.risk_tolerance ===
                          "moderate"
                        ? "bg-yellow-500 w-2/3"
                        : "bg-red-500 w-full"
                    }`}
                  ></div>
                </div>
              </div>

              {/* Learning Speed with Visual Indicator */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Learning Speed</span>
                  <span className="text-white text-sm font-medium capitalize">
                    {agentInsights.agent_personality?.learning_speed}
                  </span>
                </div>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <div
                      key={level}
                      className={`w-3 h-3 rounded-full ${
                        (agentInsights.agent_personality?.learning_speed ===
                          "slow" &&
                          level <= 2) ||
                        (agentInsights.agent_personality?.learning_speed ===
                          "normal" &&
                          level <= 3) ||
                        (agentInsights.agent_personality?.learning_speed ===
                          "fast" &&
                          level <= 4) ||
                        (agentInsights.agent_personality?.learning_speed ===
                          "very_fast" &&
                          level <= 5)
                          ? "bg-blue-500"
                          : "bg-gray-600"
                      }`}
                    ></div>
                  ))}
                </div>
              </div>

              {/* Confidence Level with Gauge */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">
                    Confidence Level
                  </span>
                  <span className="text-white text-sm font-medium capitalize">
                    {agentInsights.agent_personality?.confidence_level}
                  </span>
                </div>
                <div className="relative w-full h-8 bg-gray-700 rounded-lg overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      agentInsights.agent_personality?.confidence_level ===
                      "low"
                        ? "bg-red-500 w-1/4"
                        : agentInsights.agent_personality?.confidence_level ===
                          "medium"
                        ? "bg-yellow-500 w-1/2"
                        : agentInsights.agent_personality?.confidence_level ===
                          "high"
                        ? "bg-green-500 w-3/4"
                        : "bg-blue-500 w-full"
                    }`}
                  ></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-medium text-white">
                      {agentInsights.agent_personality?.confidence_level ===
                      "low"
                        ? "25%"
                        : agentInsights.agent_personality?.confidence_level ===
                          "medium"
                        ? "50%"
                        : agentInsights.agent_personality?.confidence_level ===
                          "high"
                        ? "75%"
                        : "100%"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Analysis with Enhanced Metrics */}
            <div className="space-y-4">
              <h4 className="text-md font-semibold text-gray-300 mb-3 flex items-center">
                <span className="mr-2">📊</span>
                Performance Analysis
              </h4>

              {/* Success Rate with Progress Circle */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Success Rate</span>
                  <span className="text-white text-sm font-medium">
                    {agentInsights.performance_analysis?.success_rate}
                  </span>
                </div>
                <div className="relative w-16 h-16 mx-auto">
                  <svg
                    className="w-16 h-16 transform -rotate-90"
                    viewBox="0 0 36 36"
                  >
                    <path
                      className="text-gray-700"
                      stroke="currentColor"
                      strokeWidth="3"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="text-green-500"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      fill="none"
                      strokeDasharray={`${
                        parseInt(
                          agentInsights.performance_analysis?.success_rate
                        ) || 0
                      }, 100`}
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-medium text-white">
                      {parseInt(
                        agentInsights.performance_analysis?.success_rate
                      ) || 0}
                      %
                    </span>
                  </div>
                </div>
              </div>

              {/* Efficiency with Status Indicator */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Efficiency</span>
                  <span
                    className={`text-sm font-medium capitalize ${
                      agentInsights.performance_analysis?.efficiency === "high"
                        ? "text-green-400"
                        : agentInsights.performance_analysis?.efficiency ===
                          "medium"
                        ? "text-yellow-400"
                        : "text-red-400"
                    }`}
                  >
                    {agentInsights.performance_analysis?.efficiency}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      agentInsights.performance_analysis?.efficiency === "high"
                        ? "bg-green-500"
                        : agentInsights.performance_analysis?.efficiency ===
                          "medium"
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                  ></div>
                  <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        agentInsights.performance_analysis?.efficiency ===
                        "high"
                          ? "bg-green-500 w-full"
                          : agentInsights.performance_analysis?.efficiency ===
                            "medium"
                          ? "bg-yellow-500 w-2/3"
                          : "bg-red-500 w-1/3"
                      }`}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Reliability with Trend Indicator */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Reliability</span>
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium capitalize text-white">
                      {agentInsights.performance_analysis?.reliability}
                    </span>
                    <span className="text-green-400 text-xs">↗</span>
                  </div>
                </div>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <div
                      key={level}
                      className={`w-2 h-4 rounded-sm ${
                        (agentInsights.performance_analysis?.reliability ===
                          "poor" &&
                          level <= 1) ||
                        (agentInsights.performance_analysis?.reliability ===
                          "fair" &&
                          level <= 2) ||
                        (agentInsights.performance_analysis?.reliability ===
                          "good" &&
                          level <= 3) ||
                        (agentInsights.performance_analysis?.reliability ===
                          "very_good" &&
                          level <= 4) ||
                        (agentInsights.performance_analysis?.reliability ===
                          "excellent" &&
                          level <= 5)
                          ? "bg-green-500"
                          : "bg-gray-600"
                      }`}
                    ></div>
                  ))}
                </div>
              </div>
            </div>

            {/* Enhanced Recommendations */}
            <div className="space-y-4">
              <h4 className="text-md font-semibold text-gray-300 mb-3 flex items-center">
                <span className="mr-2">💡</span>
                AI Recommendations
              </h4>

              {agentInsights.recommendations &&
              agentInsights.recommendations.length > 0 ? (
                <div className="space-y-3">
                  {agentInsights.recommendations.map((rec, index) => (
                    <div
                      key={index}
                      className="group p-4 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg hover:border-blue-400/50 transition-all duration-200 cursor-pointer"
                      onClick={() => handleRecommendationClick(rec, index)}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-white text-xs font-bold">
                            {index + 1}
                          </span>
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-blue-300 group-hover:text-blue-200 transition-colors">
                            {rec}
                          </p>
                          <div className="mt-2 flex items-center justify-between">
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  index === 0
                                    ? "bg-red-900/30 text-red-400"
                                    : index === 1
                                    ? "bg-yellow-900/30 text-yellow-400"
                                    : "bg-green-900/30 text-green-400"
                                }`}
                              >
                                {index === 0
                                  ? "High"
                                  : index === 1
                                  ? "Medium"
                                  : "Low"}{" "}
                                Priority
                              </span>
                              <span className="px-2 py-1 bg-gray-700/50 rounded-full text-xs">
                                {getRecommendationCategory(rec)}
                              </span>
                            </div>
                            <div className="text-xs text-gray-500">
                              Click for details →
                            </div>
                          </div>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <span className="text-blue-400 text-xs">→</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">🤖</div>
                  <p className="text-sm">No recommendations available</p>
                  <p className="text-xs">
                    Agent is analyzing system patterns...
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Additional Metrics Row */}
          <div className="mt-6 pt-6 border-t border-gray-700">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {agentMetrics?.patterns_learned || 0}
                </div>
                <div className="text-xs text-gray-400">Patterns Learned</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {agentMetrics?.learning_cycles || 0}
                </div>
                <div className="text-xs text-gray-400">Learning Cycles</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {agentMetrics?.active_clients || 0}
                </div>
                <div className="text-xs text-gray-400">Active Clients</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {agentMetrics?.recent_decisions || 0}
                </div>
                <div className="text-xs text-gray-400">Recent Decisions</div>
              </div>
            </div>
          </div>
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
                      {Array.isArray(prediction.predicted_cascade_systems) 
                        ? prediction.predicted_cascade_systems.join(", ")
                        : prediction.predicted_cascade_systems || "Multiple systems"}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-orange-600 text-white text-xs rounded-full">
                      {Math.round(
                        (prediction.confidence ||
                          prediction.prediction_confidence ||
                          0) * 100
                      )}
                      % confidence
                    </span>
                    <span className="px-2 py-1 bg-red-600 text-white text-xs rounded-full">
                      {prediction.time_to_cascade_minutes ||
                        prediction.predicted_in ||
                        0}
                      min
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-300">
                  {prediction.ai_analysis?.root_cause_analysis || 
                   prediction.summary || 
                   "Potential cascade failure detected based on current alert patterns"}
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
                              {typeof action === "string"
                                ? action
                                : action.action || action}
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

      {/* Recommendation Details Modal */}
      {showRecommendationModal && selectedRecommendation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">
                      {selectedRecommendation.id + 1}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white">
                      AI Recommendation Details
                    </h3>
                    <p className="text-sm text-gray-400">
                      {selectedRecommendation.category} •{" "}
                      {selectedRecommendation.priority} Priority
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowRecommendationModal(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {/* Recommendation Title */}
              <div className="mb-6">
                <h4 className="text-lg font-medium text-white mb-2">
                  {selectedRecommendation.title}
                </h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {selectedRecommendation.description}
                </p>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400 mb-1">Impact</div>
                  <div
                    className={`text-sm font-medium ${
                      selectedRecommendation.impact === "High"
                        ? "text-green-400"
                        : selectedRecommendation.impact === "Medium"
                        ? "text-yellow-400"
                        : "text-red-400"
                    }`}
                  >
                    {selectedRecommendation.impact}
                  </div>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400 mb-1">
                    Effort Required
                  </div>
                  <div
                    className={`text-sm font-medium ${
                      selectedRecommendation.effort === "Low"
                        ? "text-green-400"
                        : selectedRecommendation.effort === "Medium"
                        ? "text-yellow-400"
                        : "text-red-400"
                    }`}
                  >
                    {selectedRecommendation.effort}
                  </div>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400 mb-1">Timeline</div>
                  <div className="text-sm font-medium text-white">
                    {selectedRecommendation.timeline}
                  </div>
                </div>
              </div>

              {/* Implementation Actions */}
              <div className="mb-6">
                <h5 className="text-md font-semibold text-gray-300 mb-3 flex items-center">
                  <span className="mr-2">📋</span>
                  Implementation Actions
                </h5>
                <div className="space-y-2">
                  {selectedRecommendation.actions.map((action, index) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 bg-gray-700/30 rounded-lg"
                    >
                      <div className="w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-white text-xs font-bold">
                          {index + 1}
                        </span>
                      </div>
                      <span className="text-gray-300 text-sm">{action}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expected Metrics */}
              <div className="mb-6">
                <h5 className="text-md font-semibold text-gray-300 mb-3 flex items-center">
                  <span className="mr-2">📊</span>
                  Expected Impact Metrics
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(selectedRecommendation.metrics).map(
                    ([metric, value], index) => (
                      <div
                        key={index}
                        className="flex justify-between items-center p-3 bg-gray-700/30 rounded-lg"
                      >
                        <span className="text-gray-300 text-sm">{metric}</span>
                        <span className="text-green-400 text-sm font-medium">
                          {value}
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4 border-t border-gray-700">
                <button
                  onClick={() => executeRecommendation(selectedRecommendation)}
                  disabled={actionLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors font-medium"
                >
                  {actionLoading ? "Executing..." : "Execute Recommendation"}
                </button>
                <button
                  onClick={() => setShowRecommendationModal(false)}
                  className="px-4 py-2 border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentControl;
