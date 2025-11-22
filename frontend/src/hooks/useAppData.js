import { useState, useEffect } from "react";
import { apiClient } from "../utils/apiClient";

export const useAppData = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [alerts, setAlerts] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [filteredData, setFilteredData] = useState(null);

  // Simulated real-time updates
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch all data in parallel with individual error handling
        // This prevents one failing request from blocking others
        const [alertsData, predictionsData, clientsData, statsData, filteredAlerts] = await Promise.all([
          apiClient.getAllAlerts().catch(err => {
            console.error("Failed to fetch alerts:", err);
            return []; // Return empty array as fallback
          }),
          apiClient.getAllPredictions().catch(err => {
            console.error("Failed to fetch predictions:", err);
            return []; // Return empty array as fallback
          }),
          apiClient.getAllClients().catch(err => {
            console.error("Failed to fetch clients:", err);
            return []; // Return empty array as fallback
          }),
          apiClient.getAlertStats().catch(err => {
            console.error("Failed to fetch stats:", err);
            return {}; // Return empty object as fallback
          }),
          apiClient.getFilteredAlerts().catch(err => {
            console.error("Failed to fetch filtered alerts:", err);
            return null; // Return null as fallback
          }),
        ]);

        // Only set data if we got valid responses
        if (alertsData && alertsData.length !== undefined) {
          setAlerts(alertsData);
        }
        if (predictionsData && predictionsData.length !== undefined) {
          setPredictions(predictionsData);
        }
        if (clientsData && clientsData.length !== undefined) {
          setClients(clientsData);
        }
        if (statsData && typeof statsData === 'object') {
          setStats(statsData);
        }
        if (filteredAlerts !== null) {
          setFilteredData(filteredAlerts);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        // Don't show alert for individual failures - they're handled above
        // Only show if there's a critical error
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Set up real-time updates every 30 seconds
    // DISABLED: Auto-refresh commented out to allow services to scale to zero
    // Uncomment for demo mode to enable real-time updates
    // const interval = setInterval(fetchData, 30000);

    // return () => clearInterval(interval);
  }, []);

  // Show notification for high-risk predictions
  useEffect(() => {
    if (predictions.length > 0) {
      const highRiskPredictions = predictions.filter(
        (p) => p.prediction_confidence > 0.8 && p.time_to_cascade_minutes < 15
      );

      if (highRiskPredictions.length > 0) {
        // In a real app, this would be a proper notification system
        const notification = `🚨 CASCADE ALERT: ${highRiskPredictions.length} high-risk cascade predictions detected!`;

        // Show browser notification if supported
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("CascadeGuard Alert", {
            body: notification,
            icon: "/favicon.ico",
          });
        } else {
          console.log("High Risk Alert:", notification);
        }
      }
    }
  }, [predictions]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return {
    activeTab,
    alerts,
    predictions,
    clients,
    loading,
    stats,
    filteredData,
    handleTabChange,
  };
};
