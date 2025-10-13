const API_BASE_URL = "http://localhost:8000/api";

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
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
}

export const apiClient = new ApiClient();
