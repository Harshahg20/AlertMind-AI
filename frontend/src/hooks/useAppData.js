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

        // Fetch all data in parallel
        const [
          alertsData,
          predictionsData,
          clientsData,
          statsData,
          filteredAlerts,
        ] = await Promise.all([
          apiClient.getAllAlerts(),
          apiClient.getAllPredictions(),
          apiClient.getAllClients(),
          apiClient.getAlertStats(),
          apiClient.getFilteredAlerts(),
        ]);

        setAlerts(alertsData);
        setPredictions(predictionsData);
        setClients(clientsData);
        setStats(statsData);
        setFilteredData(filteredAlerts);
      } catch (error) {
        console.error("Error fetching data:", error);
        // Show user-friendly error message
        alert(
          "Unable to connect to API. Please ensure the backend is running on port 8000."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchData, 30000);

    return () => clearInterval(interval);
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
