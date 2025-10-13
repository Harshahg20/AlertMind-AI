import React from "react";
import Dashboard from "../pages/Dashboard";
import AlertFeed from "../pages/AlertFeed";
import CascadeMap from "../pages/CascadeMap";
import ClientOverview from "../pages/ClientOverview";
import AgentControl from "../pages/AgentControl";
import OperationsConsole from "../pages/OperationsConsole";

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
    case "ops":
      return <OperationsConsole />;
    case "dashboard":
      return (
        <Dashboard
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
      return (
        <CascadeMap
          predictions={predictions}
          clients={clients}
          loading={loading}
        />
      );
    case "clients":
      return (
        <ClientOverview
          clients={clients}
          alerts={alerts}
          predictions={predictions}
          loading={loading}
        />
      );
    case "agent":
      return <AgentControl />;
    default:
      return null;
  }
};

export default TabContent;
