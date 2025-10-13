import React from "react";
import Dashboard from "../component/Dashboard";
import AlertFeed from "../component/AlertFeed";
import CascadeMap from "../component/CascadeMap";
import ClientOverview from "../component/ClientOverview";

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
    default:
      return null;
  }
};

export default TabContent;
