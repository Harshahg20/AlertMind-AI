import React, { useState, useEffect } from "react";
import {
  Monitor,
  Cpu,
  MemoryStick,
  HardDrive,
  Wifi,
  RefreshCw,
  Server,
} from "lucide-react";
import { SystemHealthSkeleton } from "./SkeletonLoader";

const SystemHealthDashboard = () => {
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [serviceHealth, setServiceHealth] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  useEffect(() => {
    fetchSystemHealth();
    const interval = setInterval(fetchSystemHealth, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const fetchSystemHealth = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulate system health data (in real implementation, this would come from the backend)
      const mockSystemMetrics = {
        timestamp: new Date().toISOString(),
        cpu_percent: Math.random() * 100,
        cpu_cores: 8,
        cpu_load_avg: [Math.random() * 2, Math.random() * 2, Math.random() * 2],
        memory_total: 32 * 1024 * 1024 * 1024, // 32GB
        memory_used: Math.random() * 32 * 1024 * 1024 * 1024,
        memory_percent: Math.random() * 100,
        memory_available: Math.random() * 16 * 1024 * 1024 * 1024,
        swap_total: 8 * 1024 * 1024 * 1024, // 8GB
        swap_used: Math.random() * 8 * 1024 * 1024 * 1024,
        swap_percent: Math.random() * 100,
        disk_usage: {
          "/": {
            total: 500 * 1024 * 1024 * 1024, // 500GB
            used: Math.random() * 500 * 1024 * 1024 * 1024,
            free: Math.random() * 200 * 1024 * 1024 * 1024,
            percent: Math.random() * 100,
          },
        },
        network_io: {
          packets_recv: Math.floor(Math.random() * 1000000),
          packets_sent: Math.floor(Math.random() * 1000000),
          errin: Math.floor(Math.random() * 100),
          errout: Math.floor(Math.random() * 100),
        },
        process_count: Math.floor(Math.random() * 1000) + 500,
        boot_time: Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000, // Random uptime up to 7 days
        uptime_seconds: Math.random() * 7 * 24 * 60 * 60,
        system_info: {
          platform: "macOS 14.0",
          system: "Darwin",
          release: "23.0.0",
          machine: "arm64",
          processor: "Apple M2",
        },
      };

      const mockServiceHealth = {
        database: {
          service_name: "database",
          status: Math.random() > 0.2 ? "healthy" : "degraded",
          response_time_ms: Math.random() * 100 + 10,
          error_rate: Math.random() * 0.05,
          last_check: new Date().toISOString(),
          dependencies: ["storage", "network"],
        },
        web_server: {
          service_name: "web_server",
          status: Math.random() > 0.15 ? "healthy" : "degraded",
          response_time_ms: Math.random() * 200 + 20,
          error_rate: Math.random() * 0.02,
          last_check: new Date().toISOString(),
          dependencies: ["database", "cache"],
        },
        cache: {
          service_name: "cache",
          status: Math.random() > 0.1 ? "healthy" : "degraded",
          response_time_ms: Math.random() * 50 + 5,
          error_rate: Math.random() * 0.01,
          last_check: new Date().toISOString(),
          dependencies: ["memory"],
        },
        api_gateway: {
          service_name: "api_gateway",
          status: Math.random() > 0.25 ? "healthy" : "degraded",
          response_time_ms: Math.random() * 150 + 15,
          error_rate: Math.random() * 0.03,
          last_check: new Date().toISOString(),
          dependencies: ["web_server", "database"],
        },
      };

      setSystemMetrics(mockSystemMetrics);
      setServiceHealth(mockServiceHealth);
    } catch (err) {
      console.error("Error fetching system health:", err);
      setError("Failed to load system health data");
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (
    value,
    thresholds = { good: 80, warning: 60, critical: 40 }
  ) => {
    if (value >= thresholds.good) return "text-green-400";
    if (value >= thresholds.warning) return "text-yellow-400";
    if (value >= thresholds.critical) return "text-orange-400";
    return "text-red-400";
  };

  const getHealthBg = (
    value,
    thresholds = { good: 80, warning: 60, critical: 40 }
  ) => {
    if (value >= thresholds.good) return "bg-green-900/20";
    if (value >= thresholds.warning) return "bg-yellow-900/20";
    if (value >= thresholds.critical) return "bg-orange-900/20";
    return "bg-red-900/20";
  };

  const getServiceStatusColor = (status) => {
    switch (status) {
      case "healthy":
        return "text-green-400 bg-green-900/20";
      case "degraded":
        return "text-yellow-400 bg-yellow-900/20";
      case "critical":
        return "text-red-400 bg-red-900/20";
      default:
        return "text-gray-400 bg-gray-900/20";
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / (24 * 60 * 60));
    const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60));
    const minutes = Math.floor((seconds % (60 * 60)) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  if (loading && !systemMetrics) {
    return <SystemHealthSkeleton />;
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
            <Monitor className="w-6 h-6 mr-2" />
            System Health Dashboard
          </h2>
          <p className="text-gray-400 text-sm">
            Real-time system metrics and service health monitoring
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">Live Data</span>
          </div>
          <button
            onClick={fetchSystemHealth}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* System Overview */}
      {systemMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* CPU Usage */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <Cpu className="w-5 h-5 mr-2" />
                CPU Usage
              </h3>
              <div
                className={`w-3 h-3 rounded-full ${
                  systemMetrics.cpu_percent > 80
                    ? "bg-red-400"
                    : systemMetrics.cpu_percent > 60
                    ? "bg-yellow-400"
                    : "bg-green-400"
                }`}
              ></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Current:</span>
                <span
                  className={`font-bold ${getHealthColor(
                    systemMetrics.cpu_percent
                  )}`}
                >
                  {systemMetrics.cpu_percent.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cores:</span>
                <span className="text-white">{systemMetrics.cpu_cores}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Load Avg:</span>
                <span className="text-white">
                  {systemMetrics.cpu_load_avg
                    .map((load) => load.toFixed(2))
                    .join(", ")}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getHealthBg(
                    systemMetrics.cpu_percent
                  )}`}
                  style={{ width: `${systemMetrics.cpu_percent}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Memory Usage */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <MemoryStick className="w-5 h-5 mr-2" />
                Memory Usage
              </h3>
              <div
                className={`w-3 h-3 rounded-full ${
                  systemMetrics.memory_percent > 85
                    ? "bg-red-400"
                    : systemMetrics.memory_percent > 70
                    ? "bg-yellow-400"
                    : "bg-green-400"
                }`}
              ></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Used:</span>
                <span
                  className={`font-bold ${getHealthColor(
                    systemMetrics.memory_percent,
                    { good: 70, warning: 85, critical: 95 }
                  )}`}
                >
                  {systemMetrics.memory_percent.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total:</span>
                <span className="text-white">
                  {formatBytes(systemMetrics.memory_total)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Available:</span>
                <span className="text-white">
                  {formatBytes(systemMetrics.memory_available)}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getHealthBg(
                    systemMetrics.memory_percent,
                    { good: 70, warning: 85, critical: 95 }
                  )}`}
                  style={{ width: `${systemMetrics.memory_percent}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Disk Usage */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <HardDrive className="w-5 h-5 mr-2" />
                Disk Usage
              </h3>
              <div
                className={`w-3 h-3 rounded-full ${
                  Object.values(systemMetrics.disk_usage)[0]?.percent > 90
                    ? "bg-red-400"
                    : Object.values(systemMetrics.disk_usage)[0]?.percent > 80
                    ? "bg-yellow-400"
                    : "bg-green-400"
                }`}
              ></div>
            </div>
            <div className="space-y-3">
              {Object.entries(systemMetrics.disk_usage).map(
                ([mount, usage]) => (
                  <div key={mount}>
                    <div className="flex justify-between mb-1">
                      <span className="text-gray-400">{mount}:</span>
                      <span
                        className={`font-bold ${getHealthColor(usage.percent, {
                          good: 70,
                          warning: 80,
                          critical: 90,
                        })}`}
                      >
                        {usage.percent.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">
                        {formatBytes(usage.used)}
                      </span>
                      <span className="text-gray-500">
                        {formatBytes(usage.total)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${getHealthBg(
                          usage.percent,
                          { good: 70, warning: 80, critical: 90 }
                        )}`}
                        style={{ width: `${usage.percent}%` }}
                      ></div>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>

          {/* System Info */}
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <Server className="w-5 h-5 mr-2" />
                System Info
              </h3>
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Uptime:</span>
                <span className="text-white">
                  {formatUptime(systemMetrics.uptime_seconds)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Processes:</span>
                <span className="text-white">
                  {systemMetrics.process_count}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Platform:</span>
                <span className="text-white text-sm">
                  {systemMetrics.system_info.platform}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Architecture:</span>
                <span className="text-white text-sm">
                  {systemMetrics.system_info.machine}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Network I/O */}
      {systemMetrics && (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Wifi className="w-5 h-5 mr-2" />
            Network I/O
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400 mb-1">
                {systemMetrics.network_io.packets_recv.toLocaleString()}
              </div>
              <div className="text-gray-400 text-sm">Packets Received</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400 mb-1">
                {systemMetrics.network_io.packets_sent.toLocaleString()}
              </div>
              <div className="text-gray-400 text-sm">Packets Sent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400 mb-1">
                {systemMetrics.network_io.errin}
              </div>
              <div className="text-gray-400 text-sm">Input Errors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-400 mb-1">
                {systemMetrics.network_io.errout}
              </div>
              <div className="text-gray-400 text-sm">Output Errors</div>
            </div>
          </div>
        </div>
      )}

      {/* Service Health */}
      <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Service Health
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(serviceHealth).map(([serviceName, health]) => (
            <div key={serviceName} className="bg-gray-700/30 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-white font-medium capitalize">
                  {serviceName.replace(/_/g, " ")}
                </h4>
                <div
                  className={`px-2 py-1 rounded-full text-xs font-medium ${getServiceStatusColor(
                    health.status
                  )}`}
                >
                  {health.status.toUpperCase()}
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Response Time:</span>
                  <span className="text-white">
                    {health.response_time_ms.toFixed(1)}ms
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Error Rate:</span>
                  <span className="text-white">
                    {(health.error_rate * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Dependencies:</span>
                  <span className="text-white">
                    {health.dependencies.length}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-center text-gray-400 text-sm">
        Last updated:{" "}
        {systemMetrics
          ? new Date(systemMetrics.timestamp).toLocaleString()
          : "Never"}
      </div>
    </div>
  );
};

export default SystemHealthDashboard;
