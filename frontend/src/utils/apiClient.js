// Helper function to ensure HTTPS - MUST be called on every URL
function enforceHTTPS(url) {
  if (!url) return url;
  
  // CRITICAL: Force HTTPS for any .run.app domain - this is non-negotiable
  if (url.includes('.run.app') && url.startsWith('http://')) {
    console.warn('🔒 FORCING HTTPS for .run.app domain:', url);
    url = url.replace(/^http:\/\//i, 'https://');
  }
  
  // Also enforce HTTPS if we're running in production (HTTPS frontend)
  if (typeof window !== 'undefined') {
    const isProduction = window.location.hostname.includes('.run.app') || 
                         window.location.protocol === 'https:';
    
    if (isProduction && url.startsWith('http://') && !url.includes('localhost')) {
      console.warn('🔒 FORCING HTTPS for production environment:', url);
      url = url.replace(/^http:\/\//i, 'https://');
    }
  }
  
  return url;
}

// Runtime configuration loader
// Always use HTTPS for production (Cloud Run) and HTTP only for localhost development
function getAPIBaseURL() {
  // Priority 1: Check runtime config (injected by config.js before React loads)
  if (typeof window !== 'undefined' && window.APP_CONFIG && window.APP_CONFIG.API_URL) {
    let url = window.APP_CONFIG.API_URL;
    url = enforceHTTPS(url); // Enforce HTTPS immediately
    console.log('✅ Using runtime config API URL:', url);
    return url;
  }
  
  // Priority 2: Check build-time environment variable
  if (process.env.REACT_APP_API_URL) {
    let url = process.env.REACT_APP_API_URL;
    url = enforceHTTPS(url); // Enforce HTTPS immediately
    console.log('✅ Using build-time API URL:', url);
    return url;
  }
  
  // Priority 3: Auto-detect for Cloud Run production
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    if (hostname.includes('.run.app')) {
      // Production: ALWAYS use HTTPS (no protocol from window.location)
      if (hostname.includes('alertmind-frontend')) {
        const url = 'https://alertmind-backend-hc2rzxad5q-uc.a.run.app/api';
        console.log('✅ Auto-detected backend URL (Cloud Run):', url);
        return url; // Already HTTPS
      } else if (hostname.includes('frontend')) {
        const backendUrl = hostname.replace(/frontend/, 'backend');
        const url = `https://${backendUrl}/api`; // Force HTTPS
        console.log('✅ Auto-detected backend URL (generic):', url);
        return url;
      }
    }
  }
  
  // Priority 4: Development fallback (localhost only - HTTP is OK)
  console.log('⚠️ Using development fallback (localhost)');
  return "http://localhost:8000/api";
}

let API_BASE_URL = getAPIBaseURL(); // This already enforces HTTPS internally

// Double-check HTTPS enforcement at module load
API_BASE_URL = enforceHTTPS(API_BASE_URL);
console.log('🔗 Final API_BASE_URL (module load):', API_BASE_URL);

class ApiClient {
  async request(endpoint, options = {}) {
    // ALWAYS re-check window.APP_CONFIG and enforce HTTPS
    if (typeof window !== 'undefined' && window.APP_CONFIG && window.APP_CONFIG.API_URL) {
      API_BASE_URL = enforceHTTPS(window.APP_CONFIG.API_URL);
    }
    
    // Construct URL
    let url = `${API_BASE_URL}${endpoint}`;
    
    // CRITICAL: Always enforce HTTPS before making the request (final safety check)
    url = enforceHTTPS(url);
    
    // Final validation - throw error if still HTTP for production
    if (typeof window !== 'undefined' && window.location.hostname.includes('.run.app')) {
      if (url.startsWith('http://')) {
        console.error('❌ FATAL: URL is still HTTP for production!', url);
        url = url.replace(/^http:\/\//i, 'https://');
        console.error('✅ Fixed to HTTPS:', url);
      }
    }
    
    console.log(`API Request: ${options.method || "GET"} ${url}`);

    try {
      // For Cloud Run, use credentials: 'same-origin' or omit it since we're using simple requests
      // Only include credentials if explicitly needed
      const fetchOptions = {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
        redirect: 'follow', // Let browser handle redirects
        // Don't use credentials: 'include' by default - it can cause CORS issues
        // Only use it if backend explicitly requires it
        mode: 'cors', // Explicitly set CORS mode
      };
      
      const response = await fetch(url, fetchOptions);
      
      // Handle status 0 (network error) - this means request was blocked (CORS, network, etc.)
      if (response.status === 0 || !response.ok) {
        // Check if it's a redirect that we need to handle
        if (response.status >= 300 && response.status < 400) {
          const location = response.headers.get('Location');
          if (location) {
            const redirectUrl = enforceHTTPS(location.startsWith('http') ? location : `${API_BASE_URL}${location}`);
            console.log(`🔄 Following redirect: ${url} -> ${redirectUrl}`);
            // Retry with the redirect URL
            const redirectResponse = await fetch(redirectUrl, {
              headers: {
                "Content-Type": "application/json",
                ...options.headers,
              },
              ...options,
              credentials: 'include',
            });
            return this.handleResponse(redirectResponse, endpoint);
          }
        }
      }
      
      return this.handleResponse(response, endpoint);
    } catch (error) {
      // Check if it's a network error (fetch was blocked)
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        console.error(`❌ Network Error (CORS/Blocked): ${endpoint}`, error);
        console.error(`   Request URL: ${url}`);
        console.error(`   This usually means: CORS preflight failed, network connectivity issue, or request was blocked by browser`);
      } else {
        console.error(`API request failed: ${endpoint}`, error);
      }
      throw error;
    }
  }
  
  async handleResponse(response, endpoint) {
    // Status 0 means the request was blocked (CORS, network error, etc.)
    if (response.status === 0) {
      console.error(`❌ Network Error: Request was blocked (status: 0) for ${endpoint}`);
      console.error(`   This usually means CORS is blocking the request or network error`);
      throw new Error(
        `Network error: Request was blocked. Check CORS configuration and network connectivity.`
      );
    }
    
    console.log(`API Response: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      let errorText = '';
      try {
        errorText = await response.text();
      } catch (e) {
        errorText = `Could not read error response: ${e.message}`;
      }
      console.error(`API Error Response:`, errorText);
      throw new Error(
        `HTTP error! status: ${response.status} - ${errorText}`
      );
    }

    let data;
    try {
      data = await response.json();
      console.log(`API Success:`, data);
    } catch (e) {
      console.error(`Failed to parse JSON response:`, e);
      throw new Error(`Invalid JSON response: ${e.message}`);
    }
    return data;
  }

  // Convenience methods for common HTTP verbs
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  }

  async post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: typeof body === "string" ? body : JSON.stringify(body),
    });
  }

  async put(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: typeof body === "string" ? body : JSON.stringify(body),
    });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  }

  // Alert endpoints
  // Backend routes: /api/alerts/ (with slash), /api/alerts/filtered (no slash), etc.
  async getAllAlerts() {
    return this.request("/alerts/"); // Route is @router.get("/") so needs trailing slash
  }

  async getFilteredAlerts() {
    return this.request("/alerts/filtered"); // Route is @router.get("/filtered") so NO trailing slash
  }

  async getClientAlerts(clientId) {
    return this.request(`/alerts/client/${clientId}`); // Route is @router.get("/client/{client_id}") so NO trailing slash
  }

  async getClientAlertsWithStats(clientId) {
    return this.request(`/alerts/client/${clientId}/stats`); // Check backend route - likely no trailing slash
  }

  async getAllClients() {
    return this.request("/alerts/clients"); // Route is @router.get("/clients") so NO trailing slash
  }

  async getAlertStats() {
    return this.request("/alerts/stats"); // Route is @router.get("/stats") so NO trailing slash
  }

  // Prediction endpoints
  async getAllPredictions() {
    return this.request("/predictions/"); // Route is @router.get("/") so needs trailing slash
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

  // Enhanced Patch Management endpoints
  async getCveDatabase() {
    return this.request("/enhanced-patch/cve-database");
  }

  async analyzeCveForClient(clientId, cveId) {
    return this.request(
      `/enhanced-patch/cve-analysis/${clientId}?cve_id=${cveId}`
    );
  }

  async generatePatchPlan(clientId, cveList) {
    return this.request(`/enhanced-patch/patch-plan/${clientId}`, {
      method: "POST",
      body: JSON.stringify(cveList),
    });
  }

  async optimizeMaintenanceWindows(clientId, patchPlan) {
    return this.request(`/enhanced-patch/optimize-maintenance/${clientId}`, {
      method: "POST",
      body: JSON.stringify(patchPlan),
    });
  }

  async monitorPatchExecution(clientId, windowId) {
    return this.request(`/enhanced-patch/monitor-execution/${clientId}`, {
      method: "POST",
      body: JSON.stringify({ window_id: windowId }),
    });
  }

  // IT Administrative Tasks endpoints
  async getTaskRecommendations(clientId) {
    return this.request(`/it-admin/recommendations/${clientId}`);
  }

  async executeAdministrativeTask(clientId, taskType, priority = "medium") {
    return this.request(`/it-admin/execute/${clientId}`, {
      method: "POST",
      body: JSON.stringify({
        task_type: taskType,
        priority: priority,
      }),
    });
  }

  async bulkExecuteTasks(clientId, taskTypes) {
    return this.request(`/it-admin/bulk-execute/${clientId}`, {
      method: "POST",
      body: JSON.stringify({ task_types: taskTypes }),
    });
  }

  async generateComplianceReport(clientId) {
    return this.request(`/it-admin/compliance-report/${clientId}`);
  }

  async getTaskHistory(clientId, limit = 10) {
    return this.request(`/it-admin/task-history/${clientId}?limit=${limit}`);
  }

  async getAvailableTaskTypes() {
    return this.request("/it-admin/available-tasks");
  }
}

export const apiClient = new ApiClient();
