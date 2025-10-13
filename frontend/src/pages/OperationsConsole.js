import React, { useEffect, useState } from "react";
import { apiClient } from "../utils/apiClient";

const OperationsConsole = ({ initialClientId = "client_001" }) => {
  const [clientId, setClientId] = useState(initialClientId);
  const [stats, setStats] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [playbook, setPlaybook] = useState(null);
  const [advisories, setAdvisories] = useState(null);
  const [plan, setPlan] = useState(null);
  const [blast, setBlast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const fetchInitial = async () => {
      try {
        setLoading(true);
        // Load client-specific alerts and predictions; compute stats locally
        const [clientAlerts, clientPreds] = await Promise.all([
          apiClient.getClientAlerts(clientId),
          apiClient.getClientPredictions(clientId),
        ]);
        setAlerts(clientAlerts);
        setPredictions(clientPreds);
        // derive lightweight stats
        const total = clientAlerts.length;
        const critical = clientAlerts.filter(
          (a) => a.severity === "critical"
        ).length;
        const avgRisk =
          total > 0
            ? clientAlerts.reduce((acc, a) => acc + (a.cascade_risk || 0), 0) /
              total
            : 0;
        setStats({
          total_alerts: total,
          critical_alerts: critical,
          average_cascade_risk: avgRisk,
        });
      } catch (e) {
        console.error("OpsConsole load error", e);
      } finally {
        setLoading(false);
      }
    };
    fetchInitial();
  }, []);

  // Refetch when client changes
  useEffect(() => {
    const refetchForClient = async () => {
      try {
        setBusy(true);
        const [clientAlerts, clientPreds] = await Promise.all([
          apiClient.getClientAlerts(clientId),
          apiClient.getClientPredictions(clientId),
        ]);
        setAlerts(clientAlerts);
        setPredictions(clientPreds);
        const total = clientAlerts.length;
        const critical = clientAlerts.filter(
          (a) => a.severity === "critical"
        ).length;
        const avgRisk =
          total > 0
            ? clientAlerts.reduce((acc, a) => acc + (a.cascade_risk || 0), 0) /
              total
            : 0;
        setStats({
          total_alerts: total,
          critical_alerts: critical,
          average_cascade_risk: avgRisk,
        });
        // reset dependent panels on client change
        setPlaybook(null);
        setAdvisories(null);
        setPlan(null);
        setBlast(null);
      } catch (e) {
        console.error("OpsConsole client switch error", e);
      } finally {
        setBusy(false);
      }
    };
    refetchForClient();
  }, [clientId]);

  const genPlaybook = async () => {
    setBusy(true);
    try {
      const res = await apiClient.getResolutionPlaybook(clientId);
      setPlaybook(res.playbook || null);
    } catch (e) {
      console.error("Playbook error", e);
    } finally {
      setBusy(false);
    }
  };

  const loadAdvisories = async () => {
    setBusy(true);
    try {
      const adv = await apiClient.getPatchAdvisories(clientId);
      setAdvisories(adv);
      setPlan(null);
      setBlast(null);
    } catch (e) {
      console.error("Advisories error", e);
    } finally {
      setBusy(false);
    }
  };

  const planWindow = async () => {
    if (!advisories) return;
    setBusy(true);
    try {
      const pl = await apiClient.planPatchWindow(clientId, advisories);
      setPlan(pl);
    } catch (e) {
      console.error("Plan error", e);
    } finally {
      setBusy(false);
    }
  };

  const simulate = async (product) => {
    setBusy(true);
    try {
      const sim = await apiClient.simulateBlast(clientId, product);
      setBlast(sim);
    } catch (e) {
      console.error("Blast error", e);
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const critAlerts = alerts
    .filter((a) => a.severity === "critical")
    .slice(0, 5);
  const topPreds = predictions.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Header / Client selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">
          Unified Operations Console
        </h2>
        <div className="flex items-center gap-2">
          <select
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 text-sm"
          >
            <option value="client_001">TechCorp Solutions</option>
            <option value="client_002">FinanceFlow Inc</option>
            <option value="client_003">HealthTech Medical</option>
          </select>
          <button
            onClick={genPlaybook}
            disabled={busy}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white text-sm rounded"
          >
            {busy ? "Working..." : "AI Playbook"}
          </button>
          <button
            onClick={loadAdvisories}
            disabled={busy}
            className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm rounded"
          >
            {busy ? "Loading..." : "Load Advisories"}
          </button>
          <button
            onClick={planWindow}
            disabled={busy || !advisories}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white text-sm rounded"
          >
            {busy ? "Planning..." : "Plan Window"}
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Total Alerts</div>
          <div className="text-2xl text-white font-bold">
            {stats.total_alerts || 0}
          </div>
        </div>
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Critical Alerts</div>
          <div className="text-2xl text-red-400 font-bold">
            {stats.critical_alerts || 0}
          </div>
        </div>
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Active Predictions</div>
          <div className="text-2xl text-yellow-400 font-bold">
            {predictions.length}
          </div>
        </div>
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Avg Cascade Risk</div>
          <div className="text-2xl text-green-400 font-bold">
            {Math.round((stats.average_cascade_risk || 0) * 100)}%
          </div>
        </div>
      </div>

      {/* Two-column: Critical Alerts + Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-white font-semibold mb-2">
            Recent Critical Alerts
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {critAlerts.map((a) => (
              <div
                key={a.id}
                className="p-2 bg-red-900/10 border border-red-600/20 rounded"
              >
                <div className="flex justify-between text-sm">
                  <span className="text-red-400">{a.client_name}</span>
                  <span className="text-gray-400">
                    {new Date(a.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-white text-sm">{a.system}</div>
                <div className="text-gray-300 text-xs">{a.message}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-white font-semibold mb-2">
            High-Risk Predictions
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {topPreds.map((p, i) => (
              <div
                key={i}
                className="p-2 bg-yellow-900/10 border border-yellow-600/20 rounded"
              >
                <div className="flex justify-between text-sm">
                  <span className="text-yellow-400">
                    {Math.round(p.prediction_confidence * 100)}% •{" "}
                    {p.time_to_cascade_minutes}m
                  </span>
                  <span className="text-gray-400">
                    {(p.predicted_cascade_systems || []).join(", ")}
                  </span>
                </div>
                {p.ai_analysis?.root_cause_analysis && (
                  <div className="text-gray-300 text-xs mt-1">
                    {p.ai_analysis.root_cause_analysis}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Playbook + Patch Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-white font-semibold mb-2">
            AI Resolution Playbook
          </div>
          {playbook ? (
            <div className="space-y-2">
              <div className="text-sm text-gray-300">
                Confidence:{" "}
                <span className="text-white">
                  {Math.round((playbook.confidence || 0) * 100)}%
                </span>
              </div>
              <div className="text-sm text-gray-300">
                Similar Incidents:{" "}
                <span className="text-white">
                  {playbook.similar_incident_count || 0}
                </span>
              </div>
              <div className="text-sm text-gray-300">Recommended Steps</div>
              <ol className="list-decimal pl-5 text-sm text-gray-200">
                {(playbook.recommended_steps || []).slice(0, 6).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ol>
            </div>
          ) : (
            <div className="text-gray-400 text-sm">
              Click "AI Playbook" to generate data-driven steps.
            </div>
          )}
        </div>
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <div className="text-white font-semibold mb-2">Patch Plan</div>
          {advisories ? (
            <div className="space-y-2">
              <div className="text-sm text-gray-300">Top Advisories</div>
              <div className="space-y-2">
                {advisories.advisories.slice(0, 3).map((a, i) => (
                  <div
                    key={i}
                    className="p-2 bg-gray-900/30 rounded text-xs text-gray-300"
                  >
                    <div className="flex justify-between">
                      <span className="text-white">{a.cve}</span>
                      <span className="px-2 py-0.5 rounded bg-red-600 text-white">
                        {a.client_impact_score}
                      </span>
                    </div>
                    <div className="text-gray-400">
                      {a.product} • Sev {a.severity}
                    </div>
                    <div className="mt-1 text-blue-300">
                      {a.recommended_action}
                    </div>
                    <div className="mt-1">
                      <button
                        onClick={() => simulate(a.product)}
                        className="px-2 py-0.5 bg-purple-600 hover:bg-purple-700 text-white rounded"
                      >
                        Simulate Blast
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {plan ? (
                <div className="mt-2 text-sm text-gray-300">
                  <div>
                    Start:{" "}
                    <span className="text-white">
                      {new Date(plan.window_start).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    Duration:{" "}
                    <span className="text-white">
                      {plan.window_duration_minutes} min
                    </span>
                  </div>
                  <div>
                    Risk:{" "}
                    <span className="text-white">
                      {Math.round(plan.overall_risk_score * 100)}%
                    </span>{" "}
                    {plan.approval_required ? (
                      <span className="ml-2 px-2 py-0.5 bg-orange-600 text-white text-xs rounded">
                        Approval Required
                      </span>
                    ) : (
                      <span className="ml-2 px-2 py-0.5 bg-green-600 text-white text-xs rounded">
                        Auto
                      </span>
                    )}
                  </div>
                  <div className="mt-2 text-gray-400">Staged Rollout:</div>
                  <div className="space-y-1 text-xs">
                    {plan.staged_rollout.map((s, i) => (
                      <div key={i} className="p-2 bg-gray-900/30 rounded">
                        <div className="flex justify-between text-gray-200">
                          <span>
                            {s.product} • {s.cve}
                          </span>
                          <span className="text-gray-400">
                            ~{s.estimated_minutes}m
                          </span>
                        </div>
                        <div className="text-gray-400">
                          Pre: {s.pre_checks.join(", ")}
                        </div>
                        <div className="text-gray-400">
                          Post: {s.post_checks.join(", ")}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-gray-400 text-sm">
                  Click "Plan Window" to generate maintenance plan.
                </div>
              )}
              {blast && (
                <div className="mt-2 text-xs text-gray-300">
                  <div className="text-purple-300 mb-1">Blast Radius</div>
                  <div>
                    Target: <span className="text-white">{blast.target}</span>
                  </div>
                  <div>
                    Risk:{" "}
                    <span className="text-white">
                      {Math.round(blast.risk_score * 100)}%
                    </span>
                  </div>
                  <div>
                    Impacted:{" "}
                    <span className="text-white">
                      {blast.impacted_systems.join(", ") || "None"}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-400 text-sm">
              Click "Load Advisories" to fetch patch recommendations.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperationsConsole;
