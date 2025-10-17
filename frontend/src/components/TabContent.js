import React from "react";
import OptimizedDashboard from "./OptimizedDashboard";
import AlertFeed from "../pages/AlertFeed";
import CascadeMap from "../pages/CascadeMap";
import AgentControl from "../pages/AgentControl";
import ClientCascadeView from "./ClientCascadeView";

const TabContent = ({
  activeTab,
  alerts,
  predictions,
  clients,
  loading,
  stats,
  filteredData,
}) => {
  switch (activeTab) {
    case "dashboard":
      return (
        <OptimizedDashboard
          stats={stats}
          alerts={alerts}
          predictions={predictions}
          filteredData={filteredData}
          loading={loading}
        />
      );
    case "alerts":
      return (
        <AlertFeed
          alerts={alerts}
          filteredData={filteredData}
          loading={loading}
        />
      );
    case "cascade":
      return <ClientCascadeView clients={clients} loading={loading} />;
    case "ai":
      return <AgentControl />;
    default:
      return null;
  }
};

export default TabContent;
