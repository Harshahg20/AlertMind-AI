import React, { useState, useEffect } from "react";
import {
  Users,
  AlertTriangle,
  Clock,
  Activity,
  Shield,
  RefreshCw,
  CheckCircle,
  Brain,
  Zap,
  Target,
  BarChart3,
  Network,
  GitMerge,
  Play,
  ArrowRight,
  XCircle,
  CheckCircle2,
  Server,
} from "lucide-react";
import { apiClient } from "../utils/apiClient";
import { ClientCascadeSkeleton, SkeletonLoader } from "./SkeletonLoader";

const ClientCascadeView = ({ clients = [], loading = false }) => {
  const [selectedClient, setSelectedClient] = useState("all");
  const [clientPredictions, setClientPredictions] = useState({});
  const [enhancedPredictions, setEnhancedPredictions] = useState({});
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [activeView, setActiveView] = useState("overview"); // overview, detailed, enhanced
  const [showGraph, setShowGraph] = useState(false);

  // Use useCallback to memoize the fetch function
  const fetchAllClientPredictions = React.useCallback(async () => {
    if (!clients || clients.length === 0) return;
    
    setLoadingPredictions(true);
    try {
      // Fetch all predictions in parallel instead of sequentially
      const predictionPromises = clients.map(async (client) => {
        try {
          // Only fetch basic predictions initially - enhanced can be lazy loaded
          const basicPreds = await apiClient.getClientPredictions(client.id);
          return {
            clientId: client.id,
            predictions: Array.isArray(basicPreds) ? basicPreds : [],
            enhanced: null, // Will be loaded on demand
          };
        } catch (error) {
          console.error(`Error fetching predictions for ${client.name}:`, error);
          return {
            clientId: client.id,
            predictions: [],
            enhanced: null,
          };
        }
      });

      // Wait for all parallel requests to complete
      const results = await Promise.all(predictionPromises);

      // Build the state objects
      const predictions = {};
      const enhanced = {};
      results.forEach((result) => {
        predictions[result.clientId] = result.predictions;
        enhanced[result.clientId] = result.enhanced;
      });

      setClientPredictions(predictions);
      setEnhancedPredictions(enhanced);
    } catch (error) {
      console.error("Error fetching client predictions:", error);
      setClientPredictions({});
      setEnhancedPredictions({});
    } finally {
      setLoadingPredictions(false);
    }
  }, [clients]);
  
  useEffect(() => {
    if (clients && clients.length > 0) {
      fetchAllClientPredictions();
    }
  }, [clients, fetchAllClientPredictions]);

  // Lazy load enhanced predictions only when needed - use ref to prevent duplicate calls
  const loadingEnhancedRef = React.useRef({});
  const loadEnhancedPredictions = React.useCallback(async (clientId) => {
    // If already loaded or loading, skip
    if (enhancedPredictions[clientId] || loadingEnhancedRef.current[clientId]) {
      return;
    }

    loadingEnhancedRef.current[clientId] = true;
    setLoadingPredictions(true);
    try {
      const enhancedPred = await apiClient.simulateEnhancedAgent(clientId);
      setEnhancedPredictions((prev) => ({
        ...prev,
        [clientId]: enhancedPred,
      }));
    } catch (error) {
      console.error(`Error loading enhanced predictions for ${clientId}:`, error);
    } finally {
      loadingEnhancedRef.current[clientId] = false;
      setLoadingPredictions(false);
    }
  }, [enhancedPredictions]);

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
    const basicPreds = clientPredictions[clientId] || [];
    
    // If enhanced predictions are available, use them
    if (enhanced?.prediction) {
      const urgency = enhanced.prediction.urgency_level;
      const confidence = enhanced.prediction.confidence;

      if (urgency === "critical" && confidence > 0.8) return "critical";
      if (urgency === "high" && confidence > 0.7) return "high";
      if (urgency === "medium" && confidence > 0.6) return "medium";
      return "low";
    }
    
    // Otherwise, calculate from basic predictions
    if (basicPreds.length === 0) return "low";
    
    // Find highest risk prediction
    let maxRisk = 0;
    let criticalCount = 0;
    
    basicPreds.forEach(pred => {
      const confidence = pred.prediction_confidence || 0;
      const timeToFail = pred.time_to_cascade_minutes || 999;
      
      // Calculate risk score: higher confidence + shorter time = higher risk
      const riskScore = confidence * (1 / Math.max(timeToFail, 1));
      maxRisk = Math.max(maxRisk, riskScore);
      
      // Count critical predictions (high confidence + short time)
      if (confidence > 0.7 && timeToFail < 10) {
        criticalCount++;
      }
    });
    
    // Determine risk level based on calculations
    if (criticalCount >= 2 || maxRisk > 0.15) return "critical";
    if (criticalCount >= 1 || maxRisk > 0.08) return "high";
    if (maxRisk > 0.04) return "medium";
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

  if (loading || loadingPredictions) {
    return <ClientCascadeSkeleton />;
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
            <RefreshCw className="w-4 h-4 mr-2" />
            {loadingPredictions ? "Refreshing..." : "Refresh"}
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
      
      {/* Overview Tab Controls */}
      {activeView === "overview" && (
        <div className="flex justify-end mb-4">
          <div className="bg-gray-800/50 p-1 rounded-lg flex space-x-1">
            <button
              onClick={() => setShowGraph(false)}
              className={`px-3 py-1.5 rounded text-xs font-medium flex items-center ${
                !showGraph ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              <BarChart3 className="w-3 h-3 mr-1.5" />
              Cards
            </button>
            <button
              onClick={() => setShowGraph(true)}
              className={`px-3 py-1.5 rounded text-xs font-medium flex items-center ${
                showGraph ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              <Network className="w-3 h-3 mr-1.5" />
              Topology Map
            </button>
          </div>
        </div>
      )}

      {/* Client Risk Overview */}
      {activeView === "overview" && (
        showGraph ? (
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 min-h-[500px] relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/10 via-gray-900/0 to-gray-900/0 pointer-events-none"></div>
            
            {/* Mock Topology Visualization for Demo */}
            <div className="relative z-10 w-full h-full flex flex-col items-center justify-center space-y-12">
              <div className="flex justify-center space-x-16">
                {/* Database Layer */}
                <div className="relative group">
                  <div className="w-16 h-16 rounded-full bg-red-900/30 border-2 border-red-500 flex items-center justify-center shadow-[0_0_30px_rgba(239,68,68,0.3)] animate-pulse">
                    <Server className="w-8 h-8 text-red-400" />
                  </div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-center w-32">
                    <div className="text-sm font-bold text-red-400">Primary DB</div>
                    <div className="text-[10px] text-red-300/70">CRITICAL RISK</div>
                  </div>
                  {/* Connection Line */}
                  <div className="absolute top-1/2 left-full w-16 h-0.5 bg-gradient-to-r from-red-500/50 to-orange-500/50"></div>
                </div>
              </div>

              <div className="flex justify-center space-x-24">
                {/* App Layer */}
                <div className="relative group">
                  <div className="w-14 h-14 rounded-full bg-orange-900/30 border-2 border-orange-500 flex items-center justify-center shadow-[0_0_20px_rgba(249,115,22,0.2)]">
                    <Activity className="w-7 h-7 text-orange-400" />
                  </div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-center w-32">
                    <div className="text-sm font-bold text-orange-400">API Gateway</div>
                    <div className="text-[10px] text-orange-300/70">HIGH LATENCY</div>
                  </div>
                   {/* Connection Line Down */}
                   <div className="absolute top-full left-1/2 w-0.5 h-12 bg-gradient-to-b from-orange-500/50 to-yellow-500/50"></div>
                </div>

                <div className="relative group">
                  <div className="w-14 h-14 rounded-full bg-green-900/30 border-2 border-green-500 flex items-center justify-center">
                    <Shield className="w-7 h-7 text-green-400" />
                  </div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-center w-32">
                    <div className="text-sm font-bold text-green-400">Auth Service</div>
                    <div className="text-[10px] text-green-300/70">STABLE</div>
                  </div>
                </div>
              </div>

              <div className="flex justify-center space-x-16">
                {/* Frontend Layer */}
                <div className="relative group">
                  <div className="w-12 h-12 rounded-full bg-yellow-900/30 border-2 border-yellow-500 flex items-center justify-center">
                    <Target className="w-6 h-6 text-yellow-400" />
                  </div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-center w-32">
                    <div className="text-sm font-bold text-yellow-400">Frontend LB</div>
                    <div className="text-[10px] text-yellow-300/70">DEGRADING</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="absolute bottom-4 right-4 bg-black/40 backdrop-blur-sm p-3 rounded-lg border border-gray-700">
              <h4 className="text-xs font-semibold text-gray-300 mb-2">Legend</h4>
              <div className="space-y-1.5">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                  <span className="text-[10px] text-gray-400">Critical Failure Node</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                  <span className="text-[10px] text-gray-400">High Risk Propagation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span className="text-[10px] text-gray-400">Stable System</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
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
                            {(pred.affected_systems &&
                              pred.affected_systems.length > 0) ||
                            (pred.predicted_cascade_systems &&
                              pred.predicted_cascade_systems.length > 0)
                              ? pred.affected_systems?.[0] ||
                                pred.predicted_cascade_systems?.[0]
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
        )
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

                {loadingPredictions ? (
                  <SkeletonLoader variant="list" lines={4} height={200} />
                ) : basicPreds.length > 0 ? (
                  <>
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
                              {(prediction.affected_systems &&
                                prediction.affected_systems.length > 0) ||
                              (prediction.predicted_cascade_systems &&
                                prediction.predicted_cascade_systems.length > 0)
                                ? (
                                    prediction.affected_systems ||
                                    prediction.predicted_cascade_systems
                                  ).join(", ")
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
                  
                  {/* Predictive Timeline Visualization */}
                  <div className="mt-6 bg-gray-900/40 rounded-lg p-4 border border-gray-700">
                    <h4 className="text-sm font-medium text-white mb-4 flex items-center">
                      <Clock className="w-4 h-4 mr-2 text-blue-400" />
                      Predictive Cascade Timeline
                    </h4>
                    <div className="relative pt-6 pb-2">
                      <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-700 transform -translate-y-1/2"></div>
                      <div className="relative flex justify-between items-center px-2">
                        {[
                          { time: "Now", event: "DB Spike", severity: "medium", offset: "0%" },
                          { time: "+5m", event: "API Latency", severity: "high", offset: "25%" },
                          { time: "+12m", event: "Timeout Errors", severity: "high", offset: "60%" },
                          { time: "+20m", event: "Service Failure", severity: "critical", offset: "100%" }
                        ].map((point, i) => (
                          <div key={i} className="relative flex flex-col items-center group cursor-pointer">
                            <div className={`w-4 h-4 rounded-full border-2 z-10 ${
                              point.severity === "critical" ? "bg-red-900 border-red-500" :
                              point.severity === "high" ? "bg-orange-900 border-orange-500" :
                              "bg-yellow-900 border-yellow-500"
                            }`}></div>
                            <div className="absolute -top-8 text-xs font-mono text-gray-400 whitespace-nowrap">
                              {point.time}
                            </div>
                            <div className="absolute top-6 flex flex-col items-center w-32 text-center">
                              <span className={`text-xs font-bold ${
                                point.severity === "critical" ? "text-red-400" :
                                point.severity === "high" ? "text-orange-400" :
                                "text-yellow-400"
                              }`}>{point.event}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  </>
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

      {/* Enhanced AI View - Lazy load when tab is active */}
      {activeView === "enhanced" && (
        <EnhancedViewContent 
          clients={filteredClients}
          enhancedPredictions={enhancedPredictions}
          loadingPredictions={loadingPredictions}
          loadEnhancedPredictions={loadEnhancedPredictions}
          getUrgencyColor={getUrgencyColor}
          getConfidenceColor={getConfidenceColor}
          formatTimeToCascade={formatTimeToCascade}
        />
      )}
    </div>
  );
};

// Separate component for enhanced view with proper useEffect
const EnhancedViewContent = ({ clients, enhancedPredictions, loadingPredictions, loadEnhancedPredictions, getUrgencyColor, getConfidenceColor, formatTimeToCascade }) => {
  const loadedRef = React.useRef(false);
  const [simulationActive, setSimulationActive] = useState(false);
  
  useEffect(() => {
    // Load enhanced predictions for all clients when view becomes active (only once)
    if (!loadedRef.current && clients.length > 0) {
      loadedRef.current = true;
      clients.forEach((client) => {
        if (!enhancedPredictions[client.id] && !loadingPredictions) {
          loadEnhancedPredictions(client.id);
        }
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once when component mounts

  return (
    <div className="space-y-6">
      {clients.map((client) => {
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

                {loadingPredictions ? (
                  <SkeletonLoader variant="card" lines={8} height={400} />
                ) : enhanced?.prediction ? (
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

                    {/* Gemini War Room - Simulation Interface */}
                    {enhanced.prediction.prevention_simulation && (
                      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg p-1 border border-blue-500/30">
                        <div className="bg-gray-800/90 rounded-md p-4">
                          <div className="flex justify-between items-center mb-4">
                            <h4 className="text-lg font-medium text-white flex items-center">
                              <Brain className="w-5 h-5 mr-2 text-purple-400" />
                              Gemini War Room
                            </h4>
                            {!simulationActive ? (
                              <button
                                onClick={() => setSimulationActive(true)}
                                className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-md text-sm font-medium flex items-center transition-all"
                              >
                                <Play className="w-3 h-3 mr-1.5" />
                                Simulate Prevention
                              </button>
                            ) : (
                              <button
                                onClick={() => setSimulationActive(false)}
                                className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-md text-sm font-medium flex items-center transition-all"
                              >
                                <XCircle className="w-3 h-3 mr-1.5" />
                                Reset Simulation
                              </button>
                            )}
                          </div>

                          {simulationActive ? (
                            <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-500">
                              <div className="flex items-center justify-between bg-purple-900/20 p-3 rounded border border-purple-500/30">
                                <div className="flex items-center">
                                  <GitMerge className="w-4 h-4 text-purple-400 mr-2" />
                                  <span className="text-sm text-purple-200">
                                    Applying: <span className="font-bold">{enhanced.prediction.prevention_simulation.recommended_action}</span>
                                  </span>
                                </div>
                                <div className="text-xs text-purple-300">
                                  Est. Time Saved: {enhanced.prediction.prevention_simulation.time_saved}m
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div className="bg-red-900/10 border border-red-500/30 rounded p-3 text-center opacity-50">
                                  <div className="text-xs text-red-400 uppercase mb-1">Current Probability</div>
                                  <div className="text-2xl font-bold text-red-500">
                                    {(enhanced.prediction.confidence * 100).toFixed(0)}%
                                  </div>
                                </div>
                                <div className="flex items-center justify-center">
                                  <ArrowRight className="w-6 h-6 text-gray-500" />
                                </div>
                                <div className="bg-green-900/10 border border-green-500/30 rounded p-3 text-center transform scale-105 shadow-lg shadow-green-900/20">
                                  <div className="text-xs text-green-400 uppercase mb-1">Projected Probability</div>
                                  <div className="text-2xl font-bold text-green-500">
                                    {((enhanced.prediction.confidence * (1 - enhanced.prediction.prevention_simulation.probability_reduction)) * 100).toFixed(0)}%
                                  </div>
                                </div>
                              </div>
                              
                              <div className="text-center text-xs text-gray-400 italic">
                                "Simulation indicates significant risk reduction. Recommended for immediate execution."
                              </div>
                            </div>
                          ) : (
                            <div className="text-sm text-gray-400 text-center py-2">
                              Ready to simulate prevention strategies using Gemini 1.5 Flash models.
                            </div>
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
  );
};

export default ClientCascadeView;
