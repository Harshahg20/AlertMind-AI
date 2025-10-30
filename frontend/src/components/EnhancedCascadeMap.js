import React, { useState, useEffect } from "react";
import { Network, Activity, RefreshCw, Play, BookOpen, X } from "lucide-react";
import { apiClient } from "../utils/apiClient";
import { CascadeMapSkeleton } from "./SkeletonLoader";

const EnhancedCascadeMap = ({
  predictions = [],
  clients = [],
  loading = false,
}) => {
  const [enhancedPredictions, setEnhancedPredictions] = useState([]);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loadingEnhanced, setLoadingEnhanced] = useState(false);

  useEffect(() => {
    if (predictions.length > 0) {
      fetchEnhancedPredictions();
    }
  }, [predictions]);

  const fetchEnhancedPredictions = async () => {
    try {
      setLoadingEnhanced(true);
      const enhancedData = await apiClient.simulateEnhancedAgent("client_001");
      setEnhancedPredictions([enhancedData]);
    } catch (error) {
      console.error("Error fetching enhanced predictions:", error);
    } finally {
      setLoadingEnhanced(false);
    }
  };

  const getUrgencyLevel = (timeToCascade, confidence) => {
    if (timeToCascade <= 5 || confidence >= 0.9)
      return {
        level: "IMMEDIATE",
        color: "text-red-400",
        bg: "bg-red-900/20",
        border: "border-red-500/30",
        pulse: "animate-pulse",
      };
    if (timeToCascade <= 15 || confidence >= 0.7)
      return {
        level: "URGENT",
        color: "text-orange-400",
        bg: "bg-orange-900/20",
        border: "border-orange-500/30",
        pulse: "",
      };
    if (timeToCascade <= 30 || confidence >= 0.5)
      return {
        level: "MEDIUM",
        color: "text-yellow-400",
        bg: "bg-yellow-900/20",
        border: "border-yellow-500/30",
        pulse: "",
      };
    return {
      level: "LOW",
      color: "text-green-400",
      bg: "bg-green-900/20",
      border: "border-green-500/30",
      pulse: "",
    };
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return "text-green-400";
    if (confidence >= 0.6) return "text-yellow-400";
    return "text-red-400";
  };

  const getSystemHealthColor = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    if (score >= 40) return "text-orange-400";
    return "text-red-400";
  };

  if (loading || loadingEnhanced) {
    return <CascadeMapSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Network className="w-6 h-6 mr-2" />
            Enhanced Cascade Map
          </h2>
          <p className="text-gray-400 text-sm">
            AI-powered cascade failure prediction with comprehensive analysis
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">AI Enhanced</span>
          </div>
          <button
            onClick={fetchEnhancedPredictions}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Analysis
          </button>
        </div>
      </div>

      {/* Enhanced Predictions */}
      {enhancedPredictions.length > 0 && (
        <div className="space-y-4">
          {enhancedPredictions.map((prediction, index) => {
            const urgency = getUrgencyLevel(
              prediction.prediction?.predicted_in || 0,
              prediction.prediction?.confidence || 0
            );

            return (
              <div
                key={index}
                className={`${urgency.bg} ${urgency.border} border-2 rounded-lg p-6 ${urgency.pulse}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-4 h-4 rounded-full ${urgency.color.replace(
                        "text-",
                        "bg-"
                      )}`}
                    ></div>
                    <h3 className="text-xl font-semibold text-white">
                      {prediction.client?.name || "Unknown Client"}
                    </h3>
                  </div>
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-medium ${urgency.color} ${urgency.bg}`}
                  >
                    {urgency.level}
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">
                      Time to Cascade
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {prediction.prediction?.predicted_in || 0} minutes
                    </div>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">
                      AI Confidence
                    </div>
                    <div
                      className={`text-2xl font-bold ${getConfidenceColor(
                        prediction.prediction?.confidence || 0
                      )}`}
                    >
                      {((prediction.prediction?.confidence || 0) * 100).toFixed(
                        1
                      )}
                      %
                    </div>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">
                      System Health
                    </div>
                    <div
                      className={`text-2xl font-bold ${getSystemHealthColor(
                        prediction.system_health_score || 0
                      )}`}
                    >
                      {prediction.system_health_score || 0}/100
                    </div>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">
                      Data Sources
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {prediction.data_sources_count || 0}
                    </div>
                  </div>
                </div>

                {/* AI Analysis Quality */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">
                      AI Analysis Quality
                    </span>
                    <span className="text-blue-400 font-medium capitalize">
                      {prediction.llm_analysis_quality || "Unknown"}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{
                        width:
                          prediction.llm_analysis_quality === "excellent"
                            ? "100%"
                            : prediction.llm_analysis_quality === "good"
                            ? "75%"
                            : prediction.llm_analysis_quality === "fair"
                            ? "50%"
                            : "25%",
                      }}
                    ></div>
                  </div>
                </div>

                {/* Root Causes and Actions */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Root Causes */}
                  {prediction.prediction?.root_causes && (
                    <div className="bg-gray-800/30 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-white mb-3">
                        Root Causes
                      </h4>
                      <div className="space-y-2">
                        {prediction.prediction.root_causes.map(
                          (cause, causeIndex) => (
                            <div
                              key={causeIndex}
                              className="flex items-start space-x-3"
                            >
                              <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                              <span className="text-gray-300 text-sm">
                                {cause}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}

                  {/* Prevention Actions */}
                  {prediction.prediction?.prevention_actions && (
                    <div className="bg-gray-800/30 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-white mb-3">
                        Prevention Actions
                      </h4>
                      <div className="space-y-2">
                        {prediction.prediction.prevention_actions.map(
                          (action, actionIndex) => (
                            <div
                              key={actionIndex}
                              className="flex items-start space-x-3"
                            >
                              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                <span className="text-white text-xs font-bold">
                                  {actionIndex + 1}
                                </span>
                              </div>
                              <span className="text-gray-300 text-sm">
                                {action}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Enhanced Analysis Details */}
                {prediction.prediction?.enhanced_analysis && (
                  <div className="mt-6 bg-gray-800/30 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-white mb-3">
                      Enhanced Analysis Details
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">
                          Comprehensive Data:
                        </span>
                        <span
                          className={
                            prediction.prediction.enhanced_analysis
                              .comprehensive_data_used
                              ? "text-green-400"
                              : "text-red-400"
                          }
                        >
                          {prediction.prediction.enhanced_analysis
                            .comprehensive_data_used
                            ? "✓"
                            : "✗"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">
                          Trend Analysis:
                        </span>
                        <span
                          className={
                            prediction.prediction.enhanced_analysis
                              .trend_analysis_available
                              ? "text-green-400"
                              : "text-red-400"
                          }
                        >
                          {prediction.prediction.enhanced_analysis
                            .trend_analysis_available
                            ? "✓"
                            : "✗"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">
                          External Factors:
                        </span>
                        <span
                          className={
                            prediction.prediction.enhanced_analysis
                              .external_factors_considered
                              ? "text-green-400"
                              : "text-red-400"
                          }
                        >
                          {prediction.prediction.enhanced_analysis
                            .external_factors_considered
                            ? "✓"
                            : "✗"}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="mt-6 flex space-x-3">
                  <button
                    onClick={() => {
                      setSelectedPrediction(prediction);
                      setShowDetails(true);
                    }}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                  >
                    <BookOpen className="w-4 h-4 mr-2" />
                    View Details
                  </button>
                  <button
                    onClick={() => {
                      // Implement action execution
                      console.log(
                        "Executing prevention actions for:",
                        prediction.client?.name
                      );
                    }}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Execute Actions
                  </button>
                  <button
                    onClick={() => {
                      // Implement learning update
                      console.log(
                        "Updating agent learning for:",
                        prediction.client?.name
                      );
                    }}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                  >
                    <Activity className="w-4 h-4 mr-2" />
                    Update Learning
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Legacy Predictions (if no enhanced predictions) */}
      {enhancedPredictions.length === 0 && predictions.length > 0 && (
        <div className="space-y-4">
          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-400 rounded-full"></div>
              <span className="text-yellow-400 font-medium">
                Using Legacy Predictions
              </span>
            </div>
            <p className="text-gray-400 text-sm mt-2">
              Enhanced AI analysis is not available. Showing basic predictions.
            </p>
          </div>

          {predictions.map((prediction, index) => {
            const urgency = getUrgencyLevel(
              prediction.time_to_cascade_minutes || 0,
              prediction.prediction_confidence || 0
            );

            return (
              <div
                key={index}
                className={`${urgency.bg} ${urgency.border} border-2 rounded-lg p-6`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-white">
                    Client: {prediction.client_id}
                  </h3>
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-medium ${urgency.color} ${urgency.bg}`}
                  >
                    {urgency.level}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">
                      Time to Cascade
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {prediction.time_to_cascade_minutes || 0} minutes
                    </div>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">Confidence</div>
                    <div
                      className={`text-2xl font-bold ${getConfidenceColor(
                        prediction.prediction_confidence || 0
                      )}`}
                    >
                      {((prediction.prediction_confidence || 0) * 100).toFixed(
                        1
                      )}
                      %
                    </div>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-gray-400 text-sm mb-1">
                      Affected Systems
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {prediction.predicted_cascade_systems?.length || 0}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* No Predictions */}
      {enhancedPredictions.length === 0 && predictions.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">
            No Cascade Predictions
          </h3>
          <p className="text-gray-400 text-sm">
            No cascade failure predictions are currently available. The system
            is monitoring for potential issues.
          </p>
        </div>
      )}

      {/* Details Modal */}
      {showDetails && selectedPrediction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">
                  Detailed Analysis
                </h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Detailed content would go here */}
              <div className="space-y-6">
                <div className="bg-gray-700/50 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-3">
                    Prediction Summary
                  </h4>
                  <p className="text-gray-300">
                    {selectedPrediction.prediction?.summary ||
                      "No summary available"}
                  </p>
                </div>

                {selectedPrediction.prediction?.business_impact && (
                  <div className="bg-gray-700/50 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-white mb-3">
                      Business Impact
                    </h4>
                    <p className="text-gray-300">
                      {selectedPrediction.prediction.business_impact}
                    </p>
                  </div>
                )}

                {selectedPrediction.prediction?.reasoning && (
                  <div className="bg-gray-700/50 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-white mb-3">
                      AI Reasoning
                    </h4>
                    <div className="space-y-3">
                      {Object.entries(
                        selectedPrediction.prediction.reasoning
                      ).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-gray-400 text-sm capitalize">
                            {key.replace(/_/g, " ")}:
                          </span>
                          <span className="text-gray-300 ml-2">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedCascadeMap;
