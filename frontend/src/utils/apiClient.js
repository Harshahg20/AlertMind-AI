const API_BASE_URL = "http://localhost:8000/api";

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`API Request: ${options.method || "GET"} ${url}`);

    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      console.log(`API Response: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API Error Response:`, errorText);
        throw new Error(
          `HTTP error! status: ${response.status} - ${errorText}`
        );
      }

      const data = await response.json();
      console.log(`API Success:`, data);
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Alert endpoints
  async getAllAlerts() {
    return this.request("/alerts");
  }

  async getFilteredAlerts() {
    return this.request("/alerts/filtered");
  }

  async getClientAlerts(clientId) {
    return this.request(`/alerts/client/${clientId}`);
  }

  async getClientAlertsWithStats(clientId) {
    return this.request(`/alerts/client/${clientId}/stats`);
  }

  async getAllClients() {
    return this.request("/alerts/clients");
  }

  async getAlertStats() {
    return this.request("/alerts/stats");
  }

  // Prediction endpoints
  async getAllPredictions() {
    return this.request("/predictions");
  }

  async getClientPredictions(clientId) {
    return this.request(`/predictions/client/${clientId}`);
  }

  async getClientEnhancedPredictions(clientId) {
    return this.request(`/predictions/agent-enhanced?client_id=${clientId}`, {
      method: "POST",
    });
  }

  async getHighRiskPredictions() {
    return this.request("/predictions/high-risk");
  }

  async getCrossClientInsights() {
    return this.request("/predictions/cross-client-insights");
  }

  async getCascadeTimeline(alertId) {
    return this.request(`/predictions/cascade-timeline/${alertId}`);
  }

  async simulatePrevention(alertId, preventionAction) {
    return this.request("/predictions/simulate-prevention", {
      method: "POST",
      body: JSON.stringify({
        alert_id: alertId,
        prevention_action: preventionAction,
      }),
    });
  }

  // Enhanced Agentic AI endpoints
  async getEnhancedAgentStatus() {
    return this.request("/agent/enhanced/agent/enhanced/status");
  }

  async getEnhancedAgentInsights() {
    return this.request("/agent/enhanced/agent/enhanced/insights");
  }

  async getEnhancedAgentPerformance() {
    return this.request("/agent/enhanced/agent/enhanced/performance");
  }

  async simulateEnhancedAgent(clientId = "client_001") {
    return this.request(
      `/agent/enhanced/agent/enhanced/simulate?client_id=${clientId}`,
      {
        method: "POST",
      }
    );
  }

  async getEnhancedPredictionHistory(limit = 10) {
    return this.request(
      `/agent/enhanced/agent/enhanced/predictions/history?limit=${limit}`
    );
  }

  async getEnhancedLearnedPatterns() {
    return this.request("/agent/enhanced/agent/enhanced/patterns");
  }

  async updateEnhancedAgentLearning(incidentData) {
    return this.request("/agent/enhanced/agent/enhanced/learn", {
      method: "POST",
      body: JSON.stringify(incidentData),
    });
  }

  async predictCascadeEnhanced(correlatedData) {
    return this.request("/agent/enhanced/predict/cascade/enhanced", {
      method: "POST",
      body: JSON.stringify(correlatedData),
    });
  }

  async predictCascadeEnhancedSimple(clientId, alertsData) {
    return this.request("/agent/enhanced/predict/cascade/enhanced/simple", {
      method: "POST",
      body: JSON.stringify(alertsData),
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  // Legacy Agentic AI endpoints (for backward compatibility)
  async startAgent() {
    return this.request("/agent/start", { method: "POST" });
  }

  async stopAgent() {
    return this.request("/agent/stop", { method: "POST" });
  }

  async getAgentStatus() {
    return this.request("/agent/agent/status");
  }

  async analyzeCascadeRisk(clientId) {
    return this.request(`/agent/analyze?client_id=${clientId}`, {
      method: "POST",
    });
  }

  async executePrevention(clientId, preventionPlan) {
    return this.request("/agent/prevent", {
      method: "POST",
      body: JSON.stringify({
        client_id: clientId,
        prevention_plan: preventionPlan,
      }),
    });
  }

  async getAgentInsights() {
    return this.request("/agent/agent/insights");
  }

  async getAgentPredictions() {
    return this.request("/agent/agent/predictions/history");
  }

  async triggerAgentLearning() {
    return this.request("/agent/agent/learn", { method: "POST" });
  }

  async getAgentDecisions() {
    return this.request("/agent/decisions");
  }

  async getAgentPatterns() {
    return this.request("/agent/agent/patterns");
  }

  async getTrainingStatus() {
    return this.request("/agent/training/status");
  }

  async simulateCascade(scenario) {
    return this.request("/agent/agent/simulate", {
      method: "POST",
      body: JSON.stringify(scenario),
    });
  }

  async getResolutionPlaybook(clientId) {
    return this.request(`/agent/resolution-playbook?client_id=${clientId}`, {
      method: "POST",
    });
  }

  // Patch management endpoints
  async getPatchAdvisories(clientId) {
    return this.request(`/patch/advisories?client_id=${clientId}`);
  }

  async planPatchWindow(clientId, advisories) {
    return this.request(`/patch/plan?client_id=${clientId}`, {
      method: "POST",
      body: JSON.stringify(advisories),
    });
  }

  async simulateBlast(clientId, product) {
    return this.request(
      `/patch/simulate-blast?client_id=${clientId}&product=${encodeURIComponent(
        product
      )}`
    );
  }
}

export const apiClient = new ApiClient();
