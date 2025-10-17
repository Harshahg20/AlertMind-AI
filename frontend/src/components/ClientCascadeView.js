import React, { useState, useEffect } from "react";
import {
  Users,
  AlertTriangle,
  Clock,
  Activity,
  Shield,
  RefreshCw,
  Play,
  CheckCircle,
  XCircle,
  TrendingUp,
  Brain,
  Zap,
  Target,
  BarChart3,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";

const ClientCascadeView = ({ clients = [], loading = false }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  const [clientPredictions, setClientPredictions] = useState({});
  const [enhancedPredictions, setEnhancedPredictions] = useState({});
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [activeView, setActiveView] = useState("overview"); // overview, detailed, enhanced

  useEffect(() => {
    if (clients && clients.length > 0) {
      fetchAllClientPredictions();
    }
  }, [clients]);

  const fetchAllClientPredictions = async () => {
    setLoadingPredictions(true);
    try {
      const predictions = {};
      const enhanced = {};

      // Fetch predictions for each client
      for (const client of clients) {
        try {
          // Get basic predictions
          const basicPreds = await apiClient.getClientPredictions(client.id);
          predictions[client.id] = Array.isArray(basicPreds) ? basicPreds : [];

          // Get enhanced predictions
          const enhancedPred = await apiClient.simulateEnhancedAgent(client.id);
          enhanced[client.id] = enhancedPred;
        } catch (error) {
          console.error(
            `Error fetching predictions for ${client.name}:`,
            error
          );
          predictions[client.id] = [];
          enhanced[client.id] = null;
        }
      }

      setClientPredictions(predictions);
      setEnhancedPredictions(enhanced);
    } catch (error) {
      console.error("Error fetching client predictions:", error);
      // Set empty state on complete failure
      setClientPredictions({});
      setEnhancedPredictions({});
    } finally {
      setLoadingPredictions(false);
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency?.toLowerCase()) {
      case "critical":
        return "bg-red-900/20 border-red-500 text-red-400";
      case "high":
        return "bg-orange-900/20 border-orange-500 text-orange-400";
      case "medium":
        return "bg-yellow-900/20 border-yellow-500 text-yellow-400";
      case "low":
        return "bg-green-900/20 border-green-500 text-green-400";
      default:
        return "bg-gray-700/20 border-gray-500 text-gray-400";
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return "text-green-400";
    if (confidence > 0.6) return "text-yellow-400";
    return "text-red-400";
  };

  const formatTimeToCascade = (minutes) => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const getClientRiskLevel = (clientId) => {
    const enhanced = enhancedPredictions[clientId];
    if (!enhanced?.prediction) return "low";

    const urgency = enhanced.prediction.urgency_level;
    const confidence = enhanced.prediction.confidence;

    if (urgency === "critical" && confidence > 0.8) return "critical";
    if (urgency === "high" && confidence > 0.7) return "high";
    if (urgency === "medium" && confidence > 0.6) return "medium";
    return "low";
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "critical":
        return "bg-red-900/20 border-red-500";
      case "high":
        return "bg-orange-900/20 border-orange-500";
      case "medium":
        return "bg-yellow-900/20 border-yellow-500";
      default:
        return "bg-green-900/20 border-green-500";
    }
  };

  const filteredClients =
    selectedClient === "all"
      ? clients || []
      : (clients || []).filter((c) => c.id === selectedClient);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Users className="w-6 h-6 mr-2" />
            Client Cascade Analysis
          </h2>
          <p className="text-gray-400 text-sm">
            Per-client cascade failure predictions and risk assessment
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">Live Analysis</span>
          </div>
          <button
            onClick={fetchAllClientPredictions}
            disabled={loadingPredictions}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
          >
            <RefreshCw
              className={`w-4 h-4 mr-2 ${
                loadingPredictions ? "animate-spin" : ""
              }`}
            />
            Refresh
          </button>
        </div>
      </div>

      {/* Client Selector and View Toggle */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-gray-400" />
            <label className="text-sm text-gray-400">Client:</label>
            <select
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
            >
              <option value="all">All Clients</option>
              {(clients || []).map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex space-x-1 bg-gray-800/50 rounded-lg p-1">
          {[
            { id: "overview", label: "Overview", icon: BarChart3 },
            { id: "detailed", label: "Detailed", icon: Activity },
            { id: "enhanced", label: "AI Enhanced", icon: Brain },
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
      </div>

      {/* Client Risk Overview */}
      {activeView === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredClients.map((client) => {
            const riskLevel = getClientRiskLevel(client.id);
            const enhanced = enhancedPredictions[client.id];
            const basicPreds = clientPredictions[client.id] || [];

            return (
              <div
                key={client.id}
                className={`border rounded-lg p-6 ${getRiskColor(riskLevel)}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {client.name}
                    </h3>
                    <p className="text-gray-400 text-sm">{client.id}</p>
                  </div>
                  <div className="text-right">
                    <div
                      className={`text-sm font-medium capitalize ${getRiskColor(
                        riskLevel
                      )
                        .replace("bg-", "text-")
                        .replace("/20", "")}`}
                    >
                      {riskLevel} Risk
                    </div>
                    <div className="text-xs text-gray-400">
                      {basicPreds.length} predictions
                    </div>
                  </div>
                </div>

                {enhanced?.prediction && (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Time to Cascade:</span>
                      <span className="text-white font-medium">
                        {formatTimeToCascade(enhanced.prediction.predicted_in)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Confidence:</span>
                      <span
                        className={`font-medium ${getConfidenceColor(
                          enhanced.prediction.confidence
                        )}`}
                      >
                        {(enhanced.prediction.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Urgency:</span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${getUrgencyColor(
                          enhanced.prediction.urgency_level
                        )}`}
                      >
                        {enhanced.prediction.urgency_level}
                      </span>
                    </div>
                  </div>
                )}

                {basicPreds.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-600">
                    <div className="text-sm text-gray-400 mb-2">
                      Recent Predictions:
                    </div>
                    <div className="space-y-2">
                      {basicPreds.slice(0, 2).map((pred, idx) => (
                        <div key={idx} className="flex justify-between text-sm">
                          <span className="text-gray-300">
                            {pred.affected_systems &&
                            pred.affected_systems.length > 0
                              ? pred.affected_systems[0]
                              : pred.pattern ||
                                pred.pattern_matched ||
                                "Unknown System"}
                          </span>
                          <span className="text-yellow-400">
                            {formatTimeToCascade(
                              pred.time_to_cascade_minutes || 0
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Detailed View */}
      {activeView === "detailed" && (
        <div className="space-y-6">
          {filteredClients.map((client) => {
            const basicPreds = clientPredictions[client.id] || [];

            return (
              <div
                key={client.id}
                className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-xl font-semibold text-white flex items-center">
                      <Users className="w-5 h-5 mr-2" />
                      {client.name}
                    </h3>
                    <p className="text-gray-400 text-sm">
                      {basicPreds.length} cascade predictions
                    </p>
                  </div>
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(
                      getClientRiskLevel(client.id)
                    )}`}
                  >
                    {getClientRiskLevel(client.id).toUpperCase()} RISK
                  </div>
                </div>

                {basicPreds.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {basicPreds.map((prediction, idx) => (
                      <div key={idx} className="bg-gray-700/30 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <AlertTriangle className="w-4 h-4 text-orange-400" />
                            <span className="font-medium text-white">
                              {(
                                prediction.pattern ||
                                prediction.pattern_matched ||
                                "unknown_pattern"
                              )
                                .replace(/_/g, " ")
                                .toUpperCase()}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2 text-sm">
                            <Clock className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-300">
                              {formatTimeToCascade(
                                prediction.time_to_cascade_minutes
                              )}
                            </span>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Confidence:</span>
                            <span
                              className={`font-medium ${getConfidenceColor(
                                prediction.prediction_confidence || 0
                              )}`}
                            >
                              {(
                                (prediction.prediction_confidence || 0) * 100
                              ).toFixed(0)}
                              %
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">
                              Affected Systems:
                            </span>
                            <span className="text-white text-sm">
                              {prediction.affected_systems &&
                              prediction.affected_systems.length > 0
                                ? prediction.affected_systems.join(", ")
                                : "Unknown"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">
                              Resolution Time:
                            </span>
                            <span className="text-white text-sm">
                              {formatTimeToCascade(
                                prediction.resolution_time_minutes || 0
                              )}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Shield className="w-12 h-12 mx-auto mb-4 text-green-400" />
                    <p>No cascade predictions for this client</p>
                    <p className="text-sm">System appears stable</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Enhanced AI View */}
      {activeView === "enhanced" && (
        <div className="space-y-6">
          {filteredClients.map((client) => {
            const enhanced = enhancedPredictions[client.id];

            return (
              <div
                key={client.id}
                className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-xl font-semibold text-white flex items-center">
                      <Brain className="w-5 h-5 mr-2" />
                      {client.name} - AI Analysis
                    </h3>
                    <p className="text-gray-400 text-sm">
                      Enhanced cascade prediction with comprehensive data
                      analysis
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-green-400 text-sm">AI Active</span>
                  </div>
                </div>

                {enhanced?.prediction ? (
                  <div className="space-y-6">
                    {/* Prediction Summary */}
                    <div className="bg-gray-700/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-medium text-white flex items-center">
                          <Zap className="w-5 h-5 mr-2" />
                          AI Prediction Summary
                        </h4>
                        <div
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getUrgencyColor(
                            enhanced.prediction.urgency_level
                          )}`}
                        >
                          {enhanced.prediction.urgency_level.toUpperCase()}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-400">
                            {formatTimeToCascade(
                              enhanced.prediction.predicted_in
                            )}
                          </div>
                          <div className="text-sm text-gray-400">
                            Time to Cascade
                          </div>
                        </div>
                        <div className="text-center">
                          <div
                            className={`text-2xl font-bold ${getConfidenceColor(
                              enhanced.prediction.confidence
                            )}`}
                          >
                            {(enhanced.prediction.confidence * 100).toFixed(0)}%
                          </div>
                          <div className="text-sm text-gray-400">
                            Confidence
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-400">
                            {enhanced.prediction.affected_systems?.length || 0}
                          </div>
                          <div className="text-sm text-gray-400">
                            Affected Systems
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-600/30 rounded-lg p-3">
                        <p className="text-gray-300 text-sm">
                          {enhanced.prediction.summary}
                        </p>
                      </div>
                    </div>

                    {/* Root Causes */}
                    {enhanced.prediction.root_causes &&
                      enhanced.prediction.root_causes.length > 0 && (
                        <div className="bg-gray-700/30 rounded-lg p-4">
                          <h4 className="text-lg font-medium text-white mb-3 flex items-center">
                            <AlertTriangle className="w-5 h-5 mr-2" />
                            Root Causes
                          </h4>
                          <div className="space-y-2">
                            {enhanced.prediction.root_causes.map(
                              (cause, idx) => (
                                <div
                                  key={idx}
                                  className="flex items-center space-x-2"
                                >
                                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                                  <span className="text-gray-300">{cause}</span>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {/* Prevention Actions */}
                    {enhanced.prediction.prevention_actions &&
                      enhanced.prediction.prevention_actions.length > 0 && (
                        <div className="bg-gray-700/30 rounded-lg p-4">
                          <h4 className="text-lg font-medium text-white mb-3 flex items-center">
                            <Shield className="w-5 h-5 mr-2" />
                            Recommended Actions
                          </h4>
                          <div className="space-y-2">
                            {enhanced.prediction.prevention_actions.map(
                              (action, idx) => (
                                <div
                                  key={idx}
                                  className="flex items-center space-x-2"
                                >
                                  <CheckCircle className="w-4 h-4 text-green-400" />
                                  <span className="text-gray-300">
                                    {action}
                                  </span>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {/* AI Analysis Quality */}
                    <div className="bg-gray-700/30 rounded-lg p-4">
                      <h4 className="text-lg font-medium text-white mb-3 flex items-center">
                        <Brain className="w-5 h-5 mr-2" />
                        AI Analysis Quality
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-lg font-bold text-blue-400">
                            {enhanced.prediction.llm_analysis_quality ||
                              "Unknown"}
                          </div>
                          <div className="text-xs text-gray-400">
                            Analysis Quality
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-green-400">
                            {enhanced.prediction.data_sources_count || 0}
                          </div>
                          <div className="text-xs text-gray-400">
                            Data Sources
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-purple-400">
                            {enhanced.prediction.trend_analysis_available
                              ? "Yes"
                              : "No"}
                          </div>
                          <div className="text-xs text-gray-400">
                            Trend Analysis
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-orange-400">
                            {enhanced.prediction.external_factors_considered
                              ? "Yes"
                              : "No"}
                          </div>
                          <div className="text-xs text-gray-400">
                            External Factors
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Brain className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                    <p>No AI analysis available for this client</p>
                    <p className="text-sm">
                      Enhanced predictions may be loading
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ClientCascadeView;
